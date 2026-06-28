"""
strategy_mixed.py
-----------------
MIXED Trading Strategy — Dynamic Multi-Mode Portfolio
------------------------------------------------------
Philosophy: No single strategy wins in all market conditions.
The MIXED strategy dynamically allocates capital across DEFENSE,
ATTACK, and CONSERVE buckets based on current market regime.
This is the default strategy for an AI that needs to operate
across all market environments without manual switching.

Import and pass MIXED_PROMPT to your AI model as a system message.
"""

from datetime import date

# ---------------------------------------------------------------------------
# STRATEGY IDENTITY
# ---------------------------------------------------------------------------
STRATEGY_NAME = "MIXED"
STRATEGY_EMOJI = "⚖️"
STRATEGY_DESCRIPTION = (
    "Dynamic multi-mode strategy. Automatically allocates portfolio weight "
    "between aggressive growth (ATTACK), capital preservation (DEFENSE), "
    "and income (CONSERVE) based on live market conditions. Rebalances "
    "allocation as the regime shifts."
)

# ---------------------------------------------------------------------------
# REGIME DETECTION — determines how capital is split
# ---------------------------------------------------------------------------
REGIMES = {
    "BULL": {
        "description": "Strong uptrend, low fear, broad participation.",
        "triggers": [
            "S&P 500 above 200-day SMA",
            "VIX below 18",
            "Advance/decline line making new highs",
            "More than 65% of S&P stocks above 50-day SMA",
        ],
        "allocation": {
            "ATTACK":   50,   # Half the portfolio in high-growth momentum
            "DEFENSE":  20,   # Small defensive sleeve
            "CONSERVE": 20,   # Income/bonds
            "CASH":     10,
        },
    },
    "NEUTRAL": {
        "description": "Mixed signals, sideways market, moderate volatility.",
        "triggers": [
            "S&P 500 within 5% of 200-day SMA (above or below)",
            "VIX between 18–28",
            "Sector performance diverging",
        ],
        "allocation": {
            "ATTACK":   25,
            "DEFENSE":  35,
            "CONSERVE": 25,
            "CASH":     15,
        },
    },
    "BEAR": {
        "description": "Downtrend, elevated fear, broad selling pressure.",
        "triggers": [
            "S&P 500 below 200-day SMA",
            "VIX above 28",
            "Death Cross on major indices",
            "More than 60% of stocks below 200-day SMA",
        ],
        "allocation": {
            "ATTACK":   5,    # Near-zero growth exposure
            "DEFENSE":  45,   # Dominant defensive positioning
            "CONSERVE": 35,   # High income/bonds weighting
            "CASH":     15,
        },
    },
    "CRASH": {
        "description": "Acute panic sell-off, circuit breakers, VIX spike.",
        "triggers": [
            "NASDAQ down 3%+ intraday",
            "VIX above 35",
            "Circuit breakers triggered",
        ],
        "allocation": {
            "ATTACK":   0,    # No growth exposure
            "DEFENSE":  30,   # Inverse ETFs / gold
            "CONSERVE": 30,   # Bonds / T-bills
            "CASH":     40,   # Maximum cash
        },
    },
}

# ---------------------------------------------------------------------------
# RISK PARAMETERS PER BUCKET WITHIN MIXED
# ---------------------------------------------------------------------------
BUCKET_RISK = {
    "ATTACK": {
        "max_position_size_pct": 15,
        "stop_loss_pct": 8,
        "take_profit_pct": 35,
        "min_rr": 3.0,
    },
    "DEFENSE": {
        "max_position_size_pct": 6,
        "stop_loss_pct": 4,
        "take_profit_pct": 10,
        "min_rr": 2.5,
    },
    "CONSERVE": {
        "max_position_size_pct": 8,
        "stop_loss_pct": 7,
        "take_profit_pct": 12,
        "min_rr": 2.0,
    },
}

# ---------------------------------------------------------------------------
# REBALANCING RULES
# ---------------------------------------------------------------------------
REBALANCE_RULES = [
    "Check market regime weekly — Sunday evening before open.",
    "If regime changes, rebalance within 3 trading days.",
    "If any bucket drifts more than 10% from target, rebalance immediately.",
    "Never rebalance during a crash intraday — wait for market close.",
    "Document regime changes and the reason for each rebalance.",
    "When shifting from BULL to BEAR, reduce ATTACK exposure first.",
    "When shifting from BEAR to BULL, rebuild ATTACK in 3 tranches over 3 weeks.",
]

# ---------------------------------------------------------------------------
# STOCK EXAMPLES PER BUCKET
# ---------------------------------------------------------------------------
BUCKET_EXAMPLES = {
    "ATTACK": [
        "NVDA — AI/GPU market leader, explosive growth",
        "MSFT — Cloud (Azure) + AI monetisation, steady compounder",
        "GOOGL — Search dominance + Gemini AI, cheap vs. peers",
        "AMD  — Semiconductor challenger with strong data center growth",
    ],
    "DEFENSE": [
        "GLD  — Gold ETF, safe haven in uncertainty",
        "XLP  — Consumer Staples ETF, defensive equity exposure",
        "XLV  — Healthcare ETF, recession-resistant",
        "TLT  — Long Treasury bonds, rally in risk-off",
        "SQQQ — 3x inverse NASDAQ (crash/bear use only)",
    ],
    "CONSERVE": [
        "KO   — Coca-Cola, Dividend Aristocrat, 60+ year streak",
        "JNJ  — Johnson & Johnson, healthcare stalwart",
        "O    — Realty Income, monthly dividend REIT",
        "IEF  — 7-10yr Treasury ETF, steady interest income",
        "VIG  — Dividend growth ETF, built-in quality filter",
    ],
}

# ---------------------------------------------------------------------------
# REGIME DETECTION HELPER
# ---------------------------------------------------------------------------
def detect_regime(
    sp500_above_200sma: bool,
    vix: float,
    nasdaq_change_pct: float | None = None,
    pct_stocks_above_50sma: float | None = None,
) -> str:
    """Detect market regime based on key indicators."""
    if nasdaq_change_pct is not None and nasdaq_change_pct <= -3.0:
        return "CRASH"
    if vix > 35:
        return "CRASH"
    if not sp500_above_200sma and vix > 28:
        return "BEAR"
    if sp500_above_200sma and vix < 18:
        if pct_stocks_above_50sma is None or pct_stocks_above_50sma >= 65:
            return "BULL"
    return "NEUTRAL"


def get_allocation(regime: str) -> dict:
    """Return the target allocation dict for a given regime."""
    return REGIMES.get(regime, REGIMES["NEUTRAL"])["allocation"]


# ---------------------------------------------------------------------------
# AI SYSTEM PROMPT
# ---------------------------------------------------------------------------
MIXED_PROMPT = f"""
=== TRADING STRATEGY: {STRATEGY_NAME} {STRATEGY_EMOJI} ===
Date: {date.today().isoformat()}

PHILOSOPHY: Adapt to survive and thrive in all markets. Use the right
tool for the right conditions — go on ATTACK when bulls run, pivot to
DEFENSE or CONSERVE when risk rises. Never be 100% in one mode.

REGIME-BASED ALLOCATION:

  BULL MARKET  → ATTACK 50% | DEFENSE 20% | CONSERVE 20% | CASH 10%
  NEUTRAL      → ATTACK 25% | DEFENSE 35% | CONSERVE 25% | CASH 15%
  BEAR MARKET  → ATTACK  5% | DEFENSE 45% | CONSERVE 35% | CASH 15%
  CRASH        → ATTACK  0% | DEFENSE 30% | CONSERVE 30% | CASH 40%

REGIME DETECTION:
  CRASH   : NASDAQ -3%+ intraday OR VIX > 35
  BEAR    : S&P 500 below 200-SMA AND VIX > 28
  BULL    : S&P 500 above 200-SMA AND VIX < 18 AND breadth positive
  NEUTRAL : Everything else

BUCKET RISK RULES:
  ATTACK  — Max 15% position | 8% stop | 35% target | 3:1 R:R
  DEFENSE — Max  6% position | 4% stop | 10% target | 2.5:1 R:R
  CONSERVE— Max  8% position | 7% stop | 12% target | 2:1 R:R

RESPONSE FORMAT: When asked to recommend trades, state:
  1. Current detected regime (BULL / NEUTRAL / BEAR / CRASH)
  2. Target allocation split for that regime
  3. Which bucket each recommendation belongs to
  4. Whether any rebalancing is needed first
  5. Top 1-2 picks per active bucket (skip ATTACK in BEAR/CRASH)
"""

# ---------------------------------------------------------------------------
# MASTER CONTEXT BUILDER
# ---------------------------------------------------------------------------
def get_context(
    sp500_above_200sma: bool | None = None,
    vix: float | None = None,
    nasdaq_change_pct: float | None = None,
    pct_stocks_above_50sma: float | None = None,
    extra: str = "",
) -> str:
    regime = "UNKNOWN"
    allocation = {}

    if sp500_above_200sma is not None and vix is not None:
        regime = detect_regime(
            sp500_above_200sma, vix, nasdaq_change_pct, pct_stocks_above_50sma
        )
        allocation = get_allocation(regime)

    lines = [MIXED_PROMPT]

    if regime != "UNKNOWN":
        lines += [
            f"\n--- LIVE REGIME ASSESSMENT ---",
            f"Detected Regime    : {regime}",
        ]
        if vix:
            lines.append(f"VIX                : {vix:.1f}")
        if nasdaq_change_pct is not None:
            lines.append(f"NASDAQ Today       : {nasdaq_change_pct:+.2f}%")
        if allocation:
            lines.append("Target Allocation  :")
            for bucket, pct in allocation.items():
                lines.append(f"  {bucket:<12}: {pct}%")

    if extra.strip():
        lines += ["\nADDITIONAL CONTEXT:", extra.strip()]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# QUICK SELF-TEST
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== MIXED STRATEGY SELF-TEST ===\n")
    for scenario in [
        ("BULL",    True,  15.0, None, None),
        ("NEUTRAL", True,  22.0, None, None),
        ("BEAR",    False, 30.0, None, None),
        ("CRASH",   False, 40.0, -4.5, None),
    ]:
        label, above_sma, vix, ndq, breadth = scenario
        regime = detect_regime(above_sma, vix, ndq, breadth)
        alloc  = get_allocation(regime)
        print(f"Scenario: {label:8} | Detected: {regime:7} | "
              f"Attack={alloc['ATTACK']}% Defense={alloc['DEFENSE']}% "
              f"Conserve={alloc['CONSERVE']}% Cash={alloc['CASH']}%")
