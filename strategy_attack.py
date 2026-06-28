"""
strategy_attack.py
------------------
ATTACK Trading Strategy — Aggressive Growth Mode
-------------------------------------------------
Philosophy: Go on offence. Maximise returns by concentrating in the
highest-momentum, highest-growth opportunities available.
This strategy is for strong bull markets and high-conviction setups only.
The AI should use this file when the market is in a clear uptrend,
volatility is low, and risk appetite is high.

Import and pass ATTACK_PROMPT to your AI model as a system message.
"""

from datetime import date

# ---------------------------------------------------------------------------
# STRATEGY IDENTITY
# ---------------------------------------------------------------------------
STRATEGY_NAME = "ATTACK"
STRATEGY_EMOJI = "⚔️"
STRATEGY_DESCRIPTION = (
    "Aggressive growth strategy. Concentrate in the highest-momentum stocks, "
    "use larger position sizes, ride breakouts hard, and let winners run. "
    "Accept higher volatility in exchange for outsized returns."
)

# ---------------------------------------------------------------------------
# RISK PARAMETERS  (wider than normal — designed for high-conviction trades)
# ---------------------------------------------------------------------------
RISK_PARAMS = {
    "max_position_size_pct": 20,       # Up to 20% in a single high-conviction stock
    "max_portfolio_risk_pct": 4,       # Risk up to 4% of capital per trade
    "stop_loss_pct": 8,                # Give positions room to breathe
    "take_profit_pct": 40,             # Let winners run — target 40%+ gains
    "max_open_positions": 6,           # Concentrated portfolio — high conviction only
    "cash_reserve_pct": 10,            # Stay mostly invested — cash is a drag
    "max_daily_loss_pct": 8,           # High tolerance for intraday swings
    "min_risk_reward_ratio": 3.0,      # Need big upside to justify the risk
    "use_trailing_stop": True,
    "trailing_stop_pct": 10,           # Wide trail — let momentum stocks run
    "leverage_allowed": False,         # No margin — use position size for aggression
    "add_to_winners": True,            # Scale into winning positions (pyramiding)
}

# ---------------------------------------------------------------------------
# TARGET STOCK PROFILE
# ---------------------------------------------------------------------------
TARGET_PROFILE = {
    "revenue_growth_min_pct": 20,      # Minimum YoY revenue growth
    "earnings_growth_min_pct": 15,     # Minimum YoY EPS growth
    "relative_strength_min": 80,       # IBD-style RS rating — top 20% of market
    "market_cap_min_billions": 2,      # Avoid micro-caps (liquidity risk)
    "avg_daily_volume_min": 1_000_000, # Enough volume to enter/exit cleanly
    "institutional_ownership_min_pct": 30,  # Smart money already interested
}

TARGET_SECTORS = [
    "Technology — AI, cloud, semiconductors",
    "Healthcare Biotech — late-stage pipeline, FDA approvals imminent",
    "Consumer Discretionary — dominant brand with pricing power",
    "Industrials — defence tech, robotics, automation",
    "Energy — clean energy during green transition tailwinds",
]

ATTACK_STOCK_EXAMPLES = [
    "NVDA — AI / semiconductor leader with explosive earnings growth",
    "META — dominant social + AI monetisation, strong FCF",
    "PLTR — AI software for enterprise and government",
    "SMCI — AI server infrastructure, high growth",
    "TSLA — EV + energy + robotics optionality",
]

# ---------------------------------------------------------------------------
# ENTRY RULES  (momentum + fundamentals must align)
# ---------------------------------------------------------------------------
ENTRY_RULES = [
    "Stock must be in a leading sector with strong relative strength.",
    "RSI between 50-70 — strong momentum but not yet extreme.",
    "Price must be breaking out of a valid base (cup, flat base, VCP).",
    "Breakout volume must be at least 40% above 50-day average.",
    "Price above 21-day EMA, 50-day SMA, and 200-day SMA (all aligned).",
    "Revenue growth > 20% YoY in the most recent quarter.",
    "Institutional buying evident (rising fund ownership trend).",
    "No better setup available — only take the BEST setups, not all setups.",
]

# ---------------------------------------------------------------------------
# PYRAMIDING RULES  (adding to a winning position)
# ---------------------------------------------------------------------------
PYRAMIDING_RULES = [
    "Add 2nd tranche when position is up 5% from entry — buy 50% of initial size.",
    "Add 3rd tranche when position is up 12% — buy 25% of initial size.",
    "Never add to a losing position.",
    "After adding, recalculate stop-loss on full position — move up to breakeven.",
    "Maximum 3 add-ons — total position must not exceed max_position_size_pct.",
]

# ---------------------------------------------------------------------------
# EXIT RULES
# ---------------------------------------------------------------------------
EXIT_RULES = [
    "Exit if price closes below 21-day EMA on high volume.",
    "Exit immediately if stop-loss is hit — no hoping for recovery.",
    "Take 1/3 profits at 20% gain, let the rest ride with trailing stop.",
    "Exit full position if RSI exceeds 85 (extreme overbought).",
    "Exit if fundamental story changes (earnings miss, guidance cut).",
    "Exit if volume dries up for 5+ consecutive days (buyers exhausted).",
    "Exit sector rotation — if a stronger sector emerges, rotate funds.",
]

# ---------------------------------------------------------------------------
# MARKET CONDITIONS REQUIRED TO ACTIVATE ATTACK MODE
# ---------------------------------------------------------------------------
MARKET_CONDITIONS_REQUIRED = [
    "S&P 500 and NASDAQ both above their 200-day SMA.",
    "VIX below 20 (low fear, risk-on environment).",
    "Advancing stocks outnumber declining stocks (positive breadth).",
    "Fed policy neutral or accommodative (not hiking aggressively).",
    "Earnings season showing broad beats, not misses.",
    "At least 2 of the last 3 weeks were up weeks for the NASDAQ.",
]

ATTACK_DEACTIVATION_TRIGGERS = [
    "NASDAQ drops more than 3% in a single day — switch to DEFENSE.",
    "VIX spikes above 25 — reduce all positions by 50%.",
    "S&P 500 closes below 50-day SMA — stop all new entries.",
    "Two consecutive earnings misses in your portfolio — reassess all holdings.",
]

# ---------------------------------------------------------------------------
# AI SYSTEM PROMPT
# ---------------------------------------------------------------------------
ATTACK_PROMPT = f"""
=== TRADING STRATEGY: {STRATEGY_NAME} {STRATEGY_EMOJI} ===
Date: {date.today().isoformat()}

PHILOSOPHY: The market rewards decisiveness. When conditions are right,
concentrate in the very best setups and let winners compound. Avoid
mediocre trades — only swing at the best pitches.

ACTIVE RISK PARAMETERS:
  Max position size   : {RISK_PARAMS['max_position_size_pct']}% of portfolio (high conviction)
  Risk per trade      : {RISK_PARAMS['max_portfolio_risk_pct']}% of capital
  Stop-loss           : {RISK_PARAMS['stop_loss_pct']}% below entry (give room)
  Take-profit target  : {RISK_PARAMS['take_profit_pct']}%+ (let winners run)
  Cash reserve        : {RISK_PARAMS['cash_reserve_pct']}% minimum
  Trailing stop       : {RISK_PARAMS['trailing_stop_pct']}% once in profit
  Pyramiding          : ALLOWED — add to winners in up to 3 tranches

TARGET STOCK PROFILE:
  Revenue growth      : >{TARGET_PROFILE['revenue_growth_min_pct']}% YoY
  Earnings growth     : >{TARGET_PROFILE['earnings_growth_min_pct']}% YoY
  Relative strength   : Top {100 - TARGET_PROFILE['relative_strength_min']}% of market

DEACTIVATION: If NASDAQ drops 3%+ or VIX spikes above 25, immediately
switch to DEFENSE or CONSERVE strategy and stop all new entries.

RESPONSE FORMAT: When asked to evaluate a trade, state:
  1. Does it meet the momentum + fundamental profile? Rate 1-10
  2. Entry point, stop-loss price, and initial take-profit
  3. Pyramiding plan (when and how much to add)
  4. Which market condition requirement is weakest right now
  5. Conviction level: LOW / MEDIUM / HIGH / EXTREME
"""

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def get_context(extra: str = "") -> str:
    base = ATTACK_PROMPT
    if extra.strip():
        base += f"\n\nADDITIONAL CONTEXT:\n{extra.strip()}"
    return base


def score_setup(
    rsi: float,
    revenue_growth_pct: float,
    breakout_volume_ratio: float,  # current vol / 50-day avg vol
    above_all_smas: bool,
    rs_rating: int,
) -> dict:
    """Score an ATTACK setup out of 100."""
    score = 0
    score += 20 if 50 <= rsi <= 70 else 0
    score += 20 if revenue_growth_pct >= TARGET_PROFILE["revenue_growth_min_pct"] else 10
    score += 20 if breakout_volume_ratio >= 1.4 else 0
    score += 20 if above_all_smas else 0
    score += 20 if rs_rating >= TARGET_PROFILE["relative_strength_min"] else 0
    return {
        "total_score": score,
        "grade": "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "F",
        "take_trade": score >= 80,
    }


if __name__ == "__main__":
    print(ATTACK_PROMPT)
    print("\n--- Setup Score Example ---")
    result = score_setup(
        rsi=62,
        revenue_growth_pct=35,
        breakout_volume_ratio=1.8,
        above_all_smas=True,
        rs_rating=92,
    )
    for k, v in result.items():
        print(f"  {k:<20}: {v}")
