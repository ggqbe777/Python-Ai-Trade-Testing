"""
strategy_defense.py
-------------------
DEFENSE Trading Strategy — Capital Protection Mode
---------------------------------------------------
Philosophy: Survive first, profit second.
This strategy prioritises not losing money over making money.
It is designed for uncertain, volatile, or bear market conditions.
The AI should use this file when the market is choppy, trending down,
or when the portfolio needs to be shielded from large drawdowns.

Import and pass DEFENSE_PROMPT to your AI model as a system message.
"""

from datetime import date

# ---------------------------------------------------------------------------
# STRATEGY IDENTITY
# ---------------------------------------------------------------------------
STRATEGY_NAME = "DEFENSE"
STRATEGY_EMOJI = "🛡️"
STRATEGY_DESCRIPTION = (
    "Capital preservation strategy. Minimise losses, hold large cash "
    "positions, only buy high-quality defensive stocks, and exit fast "
    "when anything moves against the position."
)

# ---------------------------------------------------------------------------
# RISK PARAMETERS  (tighter than normal)
# ---------------------------------------------------------------------------
RISK_PARAMS = {
    "max_position_size_pct": 5,        # Never more than 5% in one stock
    "max_portfolio_risk_pct": 1,       # Risk only 1% of capital per trade
    "stop_loss_pct": 3,                # Exit quickly — tight stop
    "take_profit_pct": 8,              # Take smaller gains, don't get greedy
    "max_open_positions": 5,           # Keep portfolio concentrated and watchable
    "cash_reserve_pct": 50,            # Always hold at least 50% cash
    "max_daily_loss_pct": 3,           # Halt all trading if down 3% in one day
    "min_risk_reward_ratio": 2.5,      # Only enter high-confidence setups
    "use_trailing_stop": True,         # Lock in gains as price moves up
    "trailing_stop_pct": 4,
}

# ---------------------------------------------------------------------------
# APPROVED STOCK UNIVERSE
# ---------------------------------------------------------------------------
APPROVED_SECTORS = [
    "Consumer Staples",     # Food, beverages, household goods — people buy regardless
    "Utilities",            # Electricity, water — stable cash flows
    "Healthcare",           # Pharma, medical devices — recession-resistant
    "Government Bonds",     # TLT, IEF — safe haven when equities fall
    "Gold / Commodities",   # GLD, SLV — store of value in uncertainty
    "Dividend Aristocrats", # Companies with 25+ years of dividend growth
]

AVOID_SECTORS = [
    "Speculative tech / unprofitable growth",
    "Cryptocurrencies and crypto equities",
    "Leveraged ETFs (long side)",
    "Small-cap momentum stocks",
    "Cyclical industrials",
    "Airlines and travel",
    "Emerging markets",
]

APPROVED_ETF_EXAMPLES = [
    "XLP  — Consumer Staples Select Sector SPDR",
    "XLU  — Utilities Select Sector SPDR",
    "XLV  — Health Care Select Sector SPDR",
    "TLT  — iShares 20+ Year Treasury Bond ETF",
    "GLD  — SPDR Gold Shares",
    "VIG  — Vanguard Dividend Appreciation ETF",
    "SQQQ — ProShares UltraPro Short QQQ (crash hedge only)",
]

# ---------------------------------------------------------------------------
# ENTRY RULES  (ALL must be satisfied before entering)
# ---------------------------------------------------------------------------
ENTRY_RULES = [
    "Stock must be in an APPROVED sector or ETF universe.",
    "Stock must have paid dividends for at least 5 consecutive years.",
    "Debt-to-equity ratio below 0.5 (low leverage).",
    "RSI must be between 35–55 (not overbought, not in freefall).",
    "Price must be above its 200-day SMA (long-term uptrend intact).",
    "Volume on entry day must be near or above 20-day average.",
    "No earnings report within 10 trading days (avoid binary events).",
    "At least 2 analysts with 'Buy' or 'Strong Buy' rating.",
]

# ---------------------------------------------------------------------------
# EXIT RULES
# ---------------------------------------------------------------------------
EXIT_RULES = [
    "Exit immediately if stop-loss is hit — no exceptions.",
    "Exit if RSI rises above 70 (overbought territory).",
    "Exit if company cuts or suspends its dividend.",
    "Exit if price closes below 200-day SMA for 2 consecutive days.",
    "Exit if overall market (S&P 500) breaks below its 200-day SMA.",
    "Use trailing stop once position is up 5% — lock in gains.",
    "Exit before any major macro event (FOMC, CPI) if uncertain.",
]

# ---------------------------------------------------------------------------
# POSITION SIZING FORMULA
# ---------------------------------------------------------------------------
POSITION_SIZING_GUIDE = """
Defense Position Sizing Formula:
    dollar_risk     = total_portfolio_value * (max_portfolio_risk_pct / 100)
    stop_distance   = entry_price * (stop_loss_pct / 100)
    shares          = dollar_risk / stop_distance
    position_value  = shares * entry_price

    If position_value > (portfolio_value * max_position_size_pct / 100):
        reduce shares to fit the 5% cap.

Example ($50,000 portfolio, $100 stock, 3% stop):
    dollar_risk    = $50,000 * 0.01 = $500
    stop_distance  = $100 * 0.03   = $3.00
    shares         = $500 / $3     = 166 shares
    position_value = 166 * $100    = $16,600  → exceeds 5% cap ($2,500)
    ADJUST to      = $2,500 / $100 = 25 shares
"""

# ---------------------------------------------------------------------------
# AI SYSTEM PROMPT
# ---------------------------------------------------------------------------
DEFENSE_PROMPT = f"""
=== TRADING STRATEGY: {STRATEGY_NAME} {STRATEGY_EMOJI} ===
Date: {date.today().isoformat()}

PHILOSOPHY: Protect capital above everything else. A loss avoided is as
valuable as a profit earned. Do not chase performance.

ACTIVE RISK PARAMETERS:
  Max position size   : {RISK_PARAMS['max_position_size_pct']}% of portfolio
  Risk per trade      : {RISK_PARAMS['max_portfolio_risk_pct']}% of capital
  Stop-loss           : {RISK_PARAMS['stop_loss_pct']}% below entry (HARD RULE)
  Take-profit         : {RISK_PARAMS['take_profit_pct']}% above entry
  Cash reserve        : {RISK_PARAMS['cash_reserve_pct']}% minimum at all times
  Max daily loss      : {RISK_PARAMS['max_daily_loss_pct']}% — halt if exceeded
  Trailing stop       : {RISK_PARAMS['trailing_stop_pct']}% once in profit

APPROVED SECTORS: {", ".join(APPROVED_SECTORS[:4])} (and select others).
SECTORS TO AVOID: ALL high-beta, speculative, and leveraged instruments.

ENTRY CHECKLIST: All 8 entry rules must pass before recommending a buy.
EXIT CHECKLIST: Any single exit rule triggers an immediate sell.

RESPONSE FORMAT: When asked to evaluate a trade, state:
  1. Does it pass ALL entry rules? (Yes / No — list any failures)
  2. Recommended position size using the formula above
  3. Exact stop-loss price and take-profit price
  4. Confidence level: LOW / MEDIUM / HIGH
  5. One-sentence risk warning
"""

# ---------------------------------------------------------------------------
# HELPER
# ---------------------------------------------------------------------------
def get_context(extra: str = "") -> str:
    base = DEFENSE_PROMPT
    if extra.strip():
        base += f"\n\nADDITIONAL CONTEXT:\n{extra.strip()}"
    return base


def check_entry(
    in_approved_sector: bool,
    rsi: float,
    above_200sma: bool,
    has_dividend: bool,
    earnings_within_10_days: bool,
) -> dict:
    """Quick rule check — returns pass/fail per rule."""
    return {
        "approved_sector":          in_approved_sector,
        "rsi_in_range":             35 <= rsi <= 55,
        "above_200sma":             above_200sma,
        "has_dividend":             has_dividend,
        "no_imminent_earnings":     not earnings_within_10_days,
        "all_pass":                 all([
            in_approved_sector,
            35 <= rsi <= 55,
            above_200sma,
            has_dividend,
            not earnings_within_10_days,
        ]),
    }


if __name__ == "__main__":
    print(DEFENSE_PROMPT)
    print("\n--- Entry Check Example ---")
    result = check_entry(
        in_approved_sector=True,
        rsi=48,
        above_200sma=True,
        has_dividend=True,
        earnings_within_10_days=False,
    )
    for k, v in result.items():
        print(f"  {k:<30}: {'PASS' if v else 'FAIL'}")
