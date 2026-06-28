"""
strategy_conserve.py
--------------------
CONSERVE Trading Strategy — Income & Wealth Preservation Mode
--------------------------------------------------------------
Philosophy: Grow wealth slowly and steadily through dividends,
interest income, and low-volatility holdings. Never sacrifice
sleep for returns. This strategy is ideal for long-term wealth
building, retirement accounts, or periods of deep uncertainty.

Import and pass CONSERVE_PROMPT to your AI model as a system message.
"""

from datetime import date

# ---------------------------------------------------------------------------
# STRATEGY IDENTITY
# ---------------------------------------------------------------------------
STRATEGY_NAME = "CONSERVE"
STRATEGY_EMOJI = "🏦"
STRATEGY_DESCRIPTION = (
    "Ultra-conservative income strategy. Prioritise dividend income, "
    "bond interest, and capital stability over growth. Suitable for "
    "retirement accounts, risk-averse investors, and long-term wealth "
    "preservation regardless of market conditions."
)

# ---------------------------------------------------------------------------
# RISK PARAMETERS  (most restrictive of all strategies)
# ---------------------------------------------------------------------------
RISK_PARAMS = {
    "max_position_size_pct": 8,        # Max 8% in any single holding
    "max_portfolio_risk_pct": 0.75,    # Risk less than 1% per trade
    "stop_loss_pct": 7,                # Wider stop — hold through normal dips
    "take_profit_pct": 12,             # Modest targets; income is the goal
    "max_open_positions": 12,          # Well-diversified income portfolio
    "cash_reserve_pct": 25,            # Always keep dry powder
    "max_daily_loss_pct": 2,           # Very low pain threshold
    "min_risk_reward_ratio": 2.0,
    "rebalance_frequency": "quarterly",
    "dividend_reinvestment": True,     # DRIP — compound income automatically
    "tax_loss_harvesting": True,       # Offset gains with losses at year-end
}

# ---------------------------------------------------------------------------
# INCOME TARGET
# ---------------------------------------------------------------------------
INCOME_TARGETS = {
    "annual_yield_target_pct": 4.0,    # Target 4%+ portfolio yield
    "min_dividend_yield_pct": 2.5,     # Minimum yield for individual stocks
    "min_consecutive_dividend_years": 10,
    "preferred_payout_ratio_max_pct": 75,  # Dividend must be sustainable
}

# ---------------------------------------------------------------------------
# APPROVED ASSET CLASSES (ranked by preference)
# ---------------------------------------------------------------------------
ASSET_ALLOCATION = {
    "US_Treasury_Bonds": {
        "target_pct": 25,
        "examples": ["TLT (20yr+)", "IEF (7-10yr)", "SHY (1-3yr)"],
        "why": "Risk-free income, safe haven during equity sell-offs",
    },
    "Dividend_Aristocrats": {
        "target_pct": 30,
        "examples": ["KO (Coca-Cola)", "JNJ (Johnson & Johnson)", "PG (Procter & Gamble)", "MMM (3M)"],
        "why": "25+ years of consecutive dividend growth — proven durability",
    },
    "REITs": {
        "target_pct": 10,
        "examples": ["O (Realty Income)", "VNQ (Vanguard REIT ETF)", "SPG (Simon Property)"],
        "why": "Required to pay 90% of income as dividends — high yield",
    },
    "Preferred_Stocks": {
        "target_pct": 10,
        "examples": ["PFF (iShares Preferred ETF)", "investment-grade preferred issues"],
        "why": "Higher yield than common stock with lower volatility",
    },
    "Utility_Stocks": {
        "target_pct": 10,
        "examples": ["NEE (NextEra Energy)", "DUK (Duke Energy)", "SO (Southern Co)"],
        "why": "Regulated revenue, consistent dividends, bond-like stability",
    },
    "Cash_and_Money_Market": {
        "target_pct": 15,
        "examples": ["SGOV (T-Bill ETF)", "VMFXX (Vanguard MMF)", "high-yield savings"],
        "why": "Liquidity buffer and opportunity fund",
    },
}

# ---------------------------------------------------------------------------
# STOCK SELECTION CRITERIA
# ---------------------------------------------------------------------------
SELECTION_CRITERIA = [
    "Dividend yield >= 2.5% (income requirement).",
    "Consecutive years of dividend payments >= 10.",
    "Payout ratio <= 75% (dividend is sustainable from earnings).",
    "Debt-to-equity < 1.0 (manageable leverage).",
    "Free cash flow positive for at least 3 consecutive years.",
    "Beta <= 0.8 (lower volatility than the market).",
    "Market cap >= $10 billion (large, established company).",
    "S&P credit rating of BBB or higher (investment grade).",
]

# ---------------------------------------------------------------------------
# REBALANCING RULES
# ---------------------------------------------------------------------------
REBALANCING_RULES = [
    "Review portfolio allocation every quarter.",
    "If any asset class drifts more than 5% from target, rebalance.",
    "Reinvest all dividends automatically (DRIP) unless cash > 30%.",
    "At year-end, harvest tax losses — sell losers to offset gains.",
    "Never sell a dividend stock just because price is down — evaluate dividend safety first.",
    "Add to positions on dips of 10%+ if dividend is still safe.",
    "Replace any stock that cuts its dividend within 5 trading days.",
]

# ---------------------------------------------------------------------------
# WHAT TO AVOID
# ---------------------------------------------------------------------------
WHAT_TO_AVOID = [
    "Zero-dividend growth stocks (TSLA, NVDA, AMZN) — no income.",
    "High-yield (junk) bonds > 7% — yield is high for a reason.",
    "REITs with payout ratios > 100% — dividend is not covered.",
    "Any stock with debt-to-equity > 2.0.",
    "Speculative biotech, crypto, or SPACs.",
    "Leveraged or inverse ETFs.",
    "Companies with declining revenue for 2+ consecutive years.",
    "Any position that would cause you to lose sleep at night.",
]

# ---------------------------------------------------------------------------
# DIVIDEND SAFETY SCORECARD
# ---------------------------------------------------------------------------
def dividend_safety_score(
    payout_ratio_pct: float,
    consecutive_years: int,
    fcf_positive: bool,
    debt_to_equity: float,
    yield_pct: float,
) -> dict:
    """Score dividend safety 0-100. Above 70 = safe to hold."""
    score = 0
    score += 25 if payout_ratio_pct <= 60 else 15 if payout_ratio_pct <= 75 else 0
    score += 25 if consecutive_years >= 25 else 15 if consecutive_years >= 10 else 5
    score += 20 if fcf_positive else 0
    score += 15 if debt_to_equity <= 0.5 else 10 if debt_to_equity <= 1.0 else 0
    score += 15 if 2.5 <= yield_pct <= 5.0 else 5 if yield_pct > 5 else 0
    return {
        "score": score,
        "safety": "SAFE" if score >= 70 else "CAUTION" if score >= 45 else "DANGER",
        "hold_recommendation": score >= 70,
    }

# ---------------------------------------------------------------------------
# AI SYSTEM PROMPT
# ---------------------------------------------------------------------------
CONSERVE_PROMPT = f"""
=== TRADING STRATEGY: {STRATEGY_NAME} {STRATEGY_EMOJI} ===
Date: {date.today().isoformat()}

PHILOSOPHY: Wealth is built slowly through compounding. Prioritise
income, reinvest dividends, hold quality assets through volatility,
and never reach for yield by taking on excessive risk.

ACTIVE RISK PARAMETERS:
  Max position size   : {RISK_PARAMS['max_position_size_pct']}% per holding
  Risk per trade      : {RISK_PARAMS['max_portfolio_risk_pct']}% of capital
  Cash reserve        : {RISK_PARAMS['cash_reserve_pct']}% at all times
  Dividend yield goal : {INCOME_TARGETS['annual_yield_target_pct']}%+ annual portfolio yield
  Min dividend years  : {INCOME_TARGETS['min_consecutive_dividend_years']} consecutive years
  Rebalance           : {RISK_PARAMS['rebalance_frequency'].capitalize()}
  DRIP                : {'ENABLED' if RISK_PARAMS['dividend_reinvestment'] else 'DISABLED'}

TARGET ALLOCATION:
  Bonds (TLT/IEF)        : 25%
  Dividend Aristocrats   : 30%
  REITs                  : 10%
  Preferred Stocks       : 10%
  Utilities              : 10%
  Cash / Money Market    : 15%

SELECTION CHECKLIST: All 8 criteria must pass before recommending a buy.
AVOID LIST: Zero-dividend stocks, junk bonds, leveraged ETFs, crypto.

RESPONSE FORMAT: When asked to evaluate a holding, state:
  1. Dividend safety score (use the 5-factor scorecard)
  2. Does it fit the target allocation? Which bucket?
  3. Recommended position size
  4. Current yield and 5-year dividend growth rate
  5. Biggest risk to the dividend being maintained
"""

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def get_context(extra: str = "") -> str:
    base = CONSERVE_PROMPT
    if extra.strip():
        base += f"\n\nADDITIONAL CONTEXT:\n{extra.strip()}"
    return base


if __name__ == "__main__":
    print(CONSERVE_PROMPT)
    print("\n--- Dividend Safety Score Example ---")
    result = dividend_safety_score(
        payout_ratio_pct=55,
        consecutive_years=30,
        fcf_positive=True,
        debt_to_equity=0.4,
        yield_pct=3.2,
    )
    for k, v in result.items():
        print(f"  {k:<25}: {v}")
