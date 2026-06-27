"""
trading_reference.py
--------------------
A reference module for AI-powered trading systems.
Import this file to give your AI context about rules, strategies,
indicators, and risk management guidelines at runtime.

CRASH MODE: If the NASDAQ is experiencing a significant decline, this module
automatically defers to nasdaq_crash_protocol.py for overriding rules.
Last updated: 2026-06-27

Example usage:
    from trading_reference import RISK_RULES, INDICATOR_GUIDE, build_trading_context
    context = build_trading_context(ticker="AAPL", price=195.50, rsi=72)
    # Pass `context` as a system prompt or user message to your AI model
"""

# ---------------------------------------------------------------------------
# CRASH-MODE INTEGRATION
# ---------------------------------------------------------------------------
try:
    from nasdaq_crash_protocol import (
        is_crash,
        CRASH_RULES,
        CRASH_PROMPT,
        get_crash_summary,
        SECTOR_GUIDANCE as CRASH_SECTOR_GUIDANCE,
    )
    CRASH_PROTOCOL_AVAILABLE = True
except ImportError:
    CRASH_PROTOCOL_AVAILABLE = False

# ---------------------------------------------------------------------------
# RISK MANAGEMENT RULES
# ---------------------------------------------------------------------------
RISK_RULES = {
    "max_position_size_pct": 10,      # Max % of portfolio in a single stock
    "max_portfolio_risk_pct": 2,       # Max % of total capital at risk per trade
    "stop_loss_pct": 5,                # Default stop-loss below entry price (%)
    "take_profit_pct": 15,             # Default take-profit above entry price (%)
    "max_open_positions": 10,          # Never hold more than this many positions
    "max_daily_loss_pct": 5,           # Halt trading if daily loss exceeds this %
    "min_risk_reward_ratio": 2.0,      # Only enter trades with R:R >= 2:1
    "never_go_all_in": True,           # Always keep at least 20% cash reserve
    "cash_reserve_pct": 20,            # Minimum cash to keep uninvested
}

# ---------------------------------------------------------------------------
# TECHNICAL INDICATOR THRESHOLDS & INTERPRETATIONS
# ---------------------------------------------------------------------------
INDICATOR_GUIDE = {
    "RSI": {
        "description": "Relative Strength Index — measures momentum on a 0-100 scale.",
        "oversold_threshold": 30,
        "overbought_threshold": 70,
        "neutral_range": (40, 60),
        "rules": [
            "RSI < 30: Potential buy signal (oversold); confirm with volume.",
            "RSI > 70: Potential sell signal (overbought); watch for reversal.",
            "RSI diverging from price = early warning of trend change.",
        ],
    },
    "MACD": {
        "description": "Moving Average Convergence Divergence — trend-following momentum.",
        "rules": [
            "MACD line crosses above signal line: bullish entry signal.",
            "MACD line crosses below signal line: bearish / exit signal.",
            "Histogram expanding: trend strengthening.",
            "Histogram shrinking: trend weakening, prepare for reversal.",
        ],
    },
    "Bollinger_Bands": {
        "description": "Volatility bands set 2 standard deviations above/below a 20-day SMA.",
        "rules": [
            "Price touches lower band: potential buy in an uptrend.",
            "Price touches upper band: potential sell in a downtrend.",
            "Band squeeze (narrow width): low volatility, breakout likely soon.",
            "Band expansion: high volatility, trend in motion.",
        ],
    },
    "Volume": {
        "description": "Number of shares traded — confirms or denies price moves.",
        "rules": [
            "Price up + volume up: strong bullish confirmation.",
            "Price up + volume down: weak move, potential false breakout.",
            "Price down + volume up: strong selling pressure, avoid buying.",
            "Price down + volume down: weak selling, may be near a bottom.",
        ],
    },
    "Moving_Averages": {
        "description": "SMA/EMA smooth price data to reveal trend direction.",
        "key_levels": [20, 50, 100, 200],
        "rules": [
            "Price above 200-day SMA: long-term uptrend — prefer long positions.",
            "Price below 200-day SMA: long-term downtrend — stay cautious.",
            "Golden Cross (50 SMA crosses above 200 SMA): major bullish signal.",
            "Death Cross (50 SMA crosses below 200 SMA): major bearish signal.",
            "Price bouncing off 50-day SMA in uptrend: strong buy opportunity.",
        ],
    },
    "ATR": {
        "description": "Average True Range — measures daily volatility in price units.",
        "rules": [
            "Use 1.5–2x ATR for stop-loss placement to avoid noise.",
            "High ATR: wider stops needed, reduce position size.",
            "Low ATR: tighter stops possible, volatility breakout may be coming.",
        ],
    },
}

# ---------------------------------------------------------------------------
# TRADING STRATEGIES
# ---------------------------------------------------------------------------
STRATEGIES = {
    "momentum": {
        "description": "Buy stocks trending strongly upward; ride the momentum.",
        "entry_signals": [
            "Price above 50-day and 200-day SMA",
            "RSI between 50-70 (strong but not overbought)",
            "MACD histogram positive and expanding",
            "Volume above 20-day average on up days",
        ],
        "exit_signals": [
            "RSI exceeds 75",
            "MACD crosses below signal line",
            "Price closes below 50-day SMA",
            "Stop-loss hit",
        ],
        "best_market_conditions": "Strong bull market, sector in favor",
        "crash_mode_allowed": False,
    },
    "mean_reversion": {
        "description": "Buy oversold stocks expecting a bounce back to average.",
        "entry_signals": [
            "RSI below 30",
            "Price touches or breaks below lower Bollinger Band",
            "High volume capitulation sell-off",
            "Price at key support level",
        ],
        "exit_signals": [
            "RSI returns to 50",
            "Price reaches 20-day SMA (mean)",
            "Take-profit target hit",
        ],
        "best_market_conditions": "Sideways or range-bound market",
        "crash_mode_allowed": False,
    },
    "breakout": {
        "description": "Enter when price breaks above a resistance level with volume.",
        "entry_signals": [
            "Price closes above a multi-week resistance level",
            "Volume at least 1.5x the 20-day average on breakout candle",
            "Bollinger Band squeeze preceding the breakout",
            "RSI rising above 55 on the breakout",
        ],
        "exit_signals": [
            "Price falls back below the breakout level (failed breakout)",
            "Take-profit target hit",
            "Volume dries up after breakout (weak follow-through)",
        ],
        "best_market_conditions": "Early-to-mid bull market, high market breadth",
        "crash_mode_allowed": False,
    },
    "trend_following": {
        "description": "Stay in the direction of the dominant trend using moving averages.",
        "entry_signals": [
            "Golden Cross (50 SMA > 200 SMA)",
            "Price pulls back to and bounces off 50-day SMA",
            "MACD positive",
        ],
        "exit_signals": [
            "Death Cross (50 SMA < 200 SMA)",
            "Price breaks below 200-day SMA",
            "MACD turns negative",
        ],
        "best_market_conditions": "Sustained trending markets (up or down)",
        "crash_mode_allowed": False,
    },
    "crash_defense": {
        "description": "Capital preservation during a market crash or severe correction.",
        "entry_signals": [
            "NASDAQ drops 3 %+ intraday (crash mode triggered)",
            "VIX spikes above 35",
            "Broad market circuit breaker activated",
        ],
        "allowed_positions": [
            "Inverse ETFs: SQQQ (3x short NASDAQ), PSQ (1x short NASDAQ)",
            "Defensive sectors: Consumer Staples, Utilities, Healthcare",
            "Gold / GLD as safe haven",
            "Cash (primary position)",
        ],
        "exit_signals": [
            "VIX falls back below 25",
            "NASDAQ closes above 10-day EMA for 3 consecutive days",
            "Recovery signals confirmed (see nasdaq_crash_protocol.py)",
        ],
        "best_market_conditions": "Active crash or severe bear market",
        "crash_mode_allowed": True,
    },
}

# ---------------------------------------------------------------------------
# MARKET CONDITIONS CHECKLIST
# ---------------------------------------------------------------------------
MARKET_CONDITIONS = {
    "bullish_signs": [
        "Major indices (S&P 500, NASDAQ) above their 200-day SMA",
        "VIX (fear index) below 20",
        "Advance/decline line trending upward",
        "High percentage of stocks above their 50-day SMA (>60%)",
        "Strong earnings beats across sectors",
        "Fed in pause or rate-cutting cycle",
    ],
    "bearish_signs": [
        "Major indices below their 200-day SMA",
        "VIX above 30 (elevated fear)",
        "Inverted yield curve persisting",
        "Rising unemployment claims",
        "Earnings misses and lowered guidance widespread",
        "Fed in aggressive rate-hiking cycle",
    ],
    "neutral_caution_signs": [
        "Mixed sector performance (some up, some down)",
        "VIX between 20-30",
        "Low trading volume (summer/holiday periods)",
        "Major economic data releases imminent (CPI, NFP, FOMC)",
    ],
    "crash_signs": [
        "NASDAQ down 3 %+ intraday",
        "VIX above 35 and rising rapidly",
        "Multiple sectors selling off simultaneously",
        "Circuit breakers triggered on major exchanges",
        "High-volume panic selling with no sector sparing",
        "NASDAQ 2026-06-27: significant decline — crash protocol active",
    ],
}

# ---------------------------------------------------------------------------
# TRADE DECISION FRAMEWORK  (used to build AI prompts at runtime)
# ---------------------------------------------------------------------------
DECISION_FRAMEWORK = """
When evaluating a trade, analyze in this order:

0. CRASH CHECK — Is the NASDAQ down 3 %+ today or VIX above 35?
   If YES: switch to nasdaq_crash_protocol.py rules immediately.
   Normal steps below apply ONLY when crash mode is NOT active.

1. MARKET REGIME — Is the overall market bullish, bearish, or neutral?
   Only take long positions confidently in bullish regimes.

2. SECTOR STRENGTH — Is the stock's sector outperforming or underperforming?
   Prefer stocks in leading sectors.

3. STOCK FUNDAMENTALS — Does the company have solid revenue growth, healthy
   margins, and manageable debt? Avoid fundamentally weak stocks even on
   technical signals.

4. TECHNICAL SETUP — Do at least 3 technical indicators align with the
   intended trade direction? Never trade on a single indicator alone.

5. RISK/REWARD — Calculate potential gain vs. potential loss before entry.
   Only enter if R:R >= 2:1.

6. POSITION SIZING — Size the position so that hitting the stop-loss costs
   no more than 2% of total portfolio value.

7. CATALYSTS & TIMING — Are there upcoming earnings, Fed decisions, or
   major news events that could create outsized risk? If so, wait or
   reduce size.

8. EXIT PLAN — Define stop-loss and take-profit levels BEFORE entering.
   Never move a stop-loss in the wrong direction once set.
"""

# ---------------------------------------------------------------------------
# HELPER: BUILD A RUNTIME CONTEXT STRING FOR YOUR AI MODEL
# ---------------------------------------------------------------------------
def build_trading_context(
    ticker: str,
    price: float,
    rsi: float | None = None,
    macd_signal: str | None = None,    # "bullish", "bearish", or "neutral"
    above_200sma: bool | None = None,
    market_regime: str | None = None,  # "bullish", "bearish", "neutral", or "crash"
    nasdaq_change_pct: float | None = None,
    vix: float | None = None,
    extra_notes: str = "",
) -> str:
    """
    Build a structured context string to prepend to an AI prompt.
    Automatically switches to crash-mode rules if conditions warrant it.

    Example:
        context = build_trading_context("NVDA", 875.0, rsi=65,
                                         macd_signal="bullish",
                                         above_200sma=True,
                                         market_regime="crash",
                                         nasdaq_change_pct=-4.7,
                                         vix=38)
    """
    # Check for crash conditions
    crash_active = False
    if CRASH_PROTOCOL_AVAILABLE and nasdaq_change_pct is not None:
        crash_active = is_crash(nasdaq_change_pct, vix)
    if market_regime and market_regime.lower() == "crash":
        crash_active = True

    lines = [
        "=== TRADING REFERENCE CONTEXT ===",
        f"Ticker          : {ticker}",
        f"Current Price   : ${price:,.2f}",
        f"Date            : 2026-06-27",
    ]

    if nasdaq_change_pct is not None:
        lines.append(f"NASDAQ Today    : {nasdaq_change_pct:+.2f}%")

    if vix is not None:
        lines.append(f"VIX             : {vix:.1f}")

    if rsi is not None:
        guide = INDICATOR_GUIDE["RSI"]
        if rsi < guide["oversold_threshold"]:
            rsi_label = "OVERSOLD — potential buy signal"
        elif rsi > guide["overbought_threshold"]:
            rsi_label = "OVERBOUGHT — potential sell signal"
        else:
            rsi_label = "NEUTRAL"
        lines.append(f"RSI             : {rsi:.1f} ({rsi_label})")

    if macd_signal:
        lines.append(f"MACD Signal     : {macd_signal.upper()}")

    if above_200sma is not None:
        trend = "ABOVE 200-day SMA (long-term uptrend)" if above_200sma \
                else "BELOW 200-day SMA (long-term downtrend)"
        lines.append(f"Trend           : {trend}")

    if market_regime:
        lines.append(f"Market Regime   : {market_regime.upper()}")

    lines.append("")

    if crash_active and CRASH_PROTOCOL_AVAILABLE:
        lines += [
            "*** CRASH MODE ACTIVE — NORMAL RULES SUSPENDED ***",
            CRASH_PROMPT,
        ]
    else:
        active_rules = RISK_RULES
        lines += [
            "--- Risk Rules (Normal Mode) ---",
            f"Max position size   : {active_rules['max_position_size_pct']}% of portfolio",
            f"Stop-loss default   : {active_rules['stop_loss_pct']}% below entry",
            f"Take-profit default : {active_rules['take_profit_pct']}% above entry",
            f"Min R:R ratio       : {active_rules['min_risk_reward_ratio']}:1",
            f"Cash reserve        : {active_rules['cash_reserve_pct']}% minimum",
        ]

    lines += [
        "",
        "--- Decision Framework ---",
        DECISION_FRAMEWORK,
    ]

    if extra_notes.strip():
        lines += ["--- Additional Notes ---", extra_notes.strip()]

    lines.append("=================================")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# QUICK SELF-TEST
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Simulate today's NASDAQ crash scenario
    print("--- CRASH MODE EXAMPLE (2026-06-27) ---")
    context = build_trading_context(
        ticker="QQQ",
        price=420.00,
        rsi=28,
        macd_signal="bearish",
        above_200sma=False,
        market_regime="crash",
        nasdaq_change_pct=-4.7,
        vix=40,
        extra_notes="NASDAQ crash in progress as of 2026-06-27. Prioritise capital preservation.",
    )
    print(context)
