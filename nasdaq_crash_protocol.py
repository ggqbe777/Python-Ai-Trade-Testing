"""
nasdaq_crash_protocol.py
------------------------
AI trading reference for navigating a NASDAQ / broad market crash.
Updated: 2026-06-27

Import this module when the AI detects a significant market downturn
(NASDAQ down 3 %+ intraday or closing multi-day losing streak).
It overrides normal trading rules with defensive crash-mode settings.

Usage:
    from nasdaq_crash_protocol import CRASH_RULES, CRASH_PROMPT, is_crash
    if is_crash(nasdaq_change_pct=-4.7):
        print(CRASH_PROMPT)
"""

from datetime import date

# ---------------------------------------------------------------------------
# CRASH DETECTION THRESHOLDS
# ---------------------------------------------------------------------------
CRASH_THRESHOLDS = {
    "intraday_drop_pct": -3.0,       # NASDAQ intraday drop that triggers crash mode
    "single_day_severe_pct": -5.0,   # Severe single-day drop
    "multi_day_drawdown_pct": -10.0, # 5-day cumulative drop = correction territory
    "circuit_breaker_pct": -7.0,     # S&P 500 Level 1 circuit breaker
    "vix_spike_threshold": 35,       # VIX above this = fear spike, use crash rules
}

# ---------------------------------------------------------------------------
# CRASH-MODE RISK OVERRIDES  (replace normal RISK_RULES during a crash)
# ---------------------------------------------------------------------------
CRASH_RULES = {
    "max_position_size_pct": 3,        # Cut normal 10 % limit to 3 %
    "max_portfolio_risk_pct": 0.5,     # Risk only 0.5 % per trade (was 2 %)
    "stop_loss_pct": 3,                # Tighter stops — crashes move fast
    "take_profit_pct": 6,              # Smaller targets; take profits quickly
    "max_open_positions": 3,           # Drastically reduce exposure
    "max_daily_loss_pct": 2,           # Halt AI trading if down 2 % in a day
    "min_risk_reward_ratio": 3.0,      # Require higher R:R to justify any trade
    "cash_reserve_pct": 60,            # Hold at least 60 % cash during crash
    "shorting_allowed": True,          # Inverse ETFs (SQQQ, PSQ) permitted
    "new_long_entries_allowed": False, # No new long positions until stabilisation
    "mode": "CAPITAL_PRESERVATION",
}

# ---------------------------------------------------------------------------
# SECTORS TO AVOID vs. SECTORS THAT HOLD UP IN A NASDAQ CRASH
# ---------------------------------------------------------------------------
SECTOR_GUIDANCE = {
    "avoid": [
        "High-growth / unprofitable tech (ARK-type names)",
        "Semiconductors (highly cyclical)",
        "Speculative small-cap biotech",
        "Leveraged ETFs (long side)",
        "Crypto-adjacent equities",
        "High-multiple SaaS with no earnings",
    ],
    "defensive_refuge": [
        "Consumer Staples (KO, PG, WMT)",
        "Utilities (NEE, DUK)",
        "Healthcare / Pharma (JNJ, ABBV)",
        "Gold miners (GLD, GDX) — if USD weakening",
        "Short / inverse NASDAQ ETFs: SQQQ (3x), PSQ (1x)",
        "Treasury bonds / TLT — if Fed expected to cut",
        "Cash (USD) — always the safest crash hedge",
    ],
    "opportunistic_after_stabilisation": [
        "Quality large-cap tech with strong balance sheets (AAPL, MSFT, GOOGL)",
        "Dividend-paying blue chips beaten down unfairly",
        "Sector leaders with > 20 % free cash flow margins",
    ],
}

# ---------------------------------------------------------------------------
# CRASH PLAYBOOK — STEP BY STEP
# ---------------------------------------------------------------------------
CRASH_PLAYBOOK = [
    "STEP 1 — STOP new long entries immediately. Do not buy the first dip.",
    "STEP 2 — Review all open positions; cut anything below its stop-loss NOW.",
    "STEP 3 — Reduce position sizes across the board to crash-mode limits (3 %).",
    "STEP 4 — Raise cash to at least 60 % of portfolio.",
    "STEP 5 — Evaluate inverse ETF hedge (SQQQ, PSQ) sized to 5-10 % of portfolio.",
    "STEP 6 — Monitor VIX hourly. VIX > 40 often signals capitulation is near.",
    "STEP 7 — Watch for 3 consecutive closes without new lows = potential bottom.",
    "STEP 8 — Wait for NASDAQ to reclaim its 10-day EMA before adding any longs.",
    "STEP 9 — Re-enter slowly: buy quality names in 3 tranches, not all at once.",
    "STEP 10 — Review macro cause of crash; don't buy back into a structural bear.",
]

# ---------------------------------------------------------------------------
# HISTORICAL CRASH CONTEXT (for AI reference)
# ---------------------------------------------------------------------------
HISTORICAL_CRASHES = [
    {
        "event": "Dot-com Bust",
        "period": "2000–2002",
        "nasdaq_peak_to_trough": "-78%",
        "duration_months": 30,
        "lesson": "Valuations matter. High P/S ratio stocks fell the hardest.",
    },
    {
        "event": "Global Financial Crisis",
        "period": "2008–2009",
        "nasdaq_peak_to_trough": "-55%",
        "duration_months": 17,
        "lesson": "Credit contagion spreads to all sectors. Cash was king.",
    },
    {
        "event": "COVID Crash",
        "period": "Feb–Mar 2020",
        "nasdaq_peak_to_trough": "-32%",
        "duration_months": 1.5,
        "lesson": "V-shaped recovery possible with massive stimulus. Don't stay short too long.",
    },
    {
        "event": "2022 Rate Hike Bear Market",
        "period": "Jan–Oct 2022",
        "nasdaq_peak_to_trough": "-36%",
        "duration_months": 9,
        "lesson": "Rising rates destroy high-multiple growth stocks fastest.",
    },
]

# ---------------------------------------------------------------------------
# RECOVERY SIGNALS — WHEN TO SWITCH BACK TO NORMAL TRADING MODE
# ---------------------------------------------------------------------------
RECOVERY_SIGNALS = [
    "NASDAQ closes above its 10-day EMA for 3 consecutive days",
    "VIX falls back below 25 and is declining",
    "Advance/decline ratio turns positive (more stocks rising than falling)",
    "High-volume accumulation days outnumber distribution days over 2 weeks",
    "Fed signals a pivot or pause in rate hikes",
    "Credit spreads (HYG vs IEF) begin narrowing",
    "S&P 500 reclaims its 50-day SMA on above-average volume",
]

# ---------------------------------------------------------------------------
# AI PROMPT — inject this as system context during a crash
# ---------------------------------------------------------------------------
CRASH_PROMPT = f"""
=== MARKET CRASH MODE ACTIVE — {date.today().isoformat()} ===

The NASDAQ is experiencing a significant decline today. All normal trading
rules are SUSPENDED and replaced with the crash-mode protocol below.

PRIMARY DIRECTIVE: PRESERVE CAPITAL. Do not attempt to catch falling knives.

ACTIVE CRASH RULES:
- Maximum position size   : {CRASH_RULES['max_position_size_pct']}% of portfolio
- Risk per trade          : {CRASH_RULES['max_portfolio_risk_pct']}% of capital
- Stop-loss               : {CRASH_RULES['stop_loss_pct']}% below entry (tight)
- Minimum cash reserve    : {CRASH_RULES['cash_reserve_pct']}%
- New long entries        : {"ALLOWED" if CRASH_RULES['new_long_entries_allowed'] else "PROHIBITED"}
- Short / inverse ETFs    : {"ALLOWED" if CRASH_RULES['shorting_allowed'] else "NOT ALLOWED"}
- Mode                    : {CRASH_RULES['mode']}

SECTORS TO AVOID: {", ".join(SECTOR_GUIDANCE['avoid'][:4])} (and others).
DEFENSIVE PLAYS : {", ".join(SECTOR_GUIDANCE['defensive_refuge'][:4])} (see full list).

CRASH PLAYBOOK: Follow the 10-step playbook in order. Do not skip steps.

Do not give BUY recommendations for speculative, high-beta, or unprofitable
growth stocks until recovery signals confirm the bottom is in.

When asked to evaluate a trade, first state whether crash-mode rules
prohibit it, then explain the risk/reward under current conditions.
=================================================================
"""

# ---------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------
def is_crash(nasdaq_change_pct: float, vix: float | None = None) -> bool:
    """Return True if current conditions trigger crash-mode trading rules."""
    triggered_by_price = nasdaq_change_pct <= CRASH_THRESHOLDS["intraday_drop_pct"]
    triggered_by_vix = (vix is not None and vix >= CRASH_THRESHOLDS["vix_spike_threshold"])
    return triggered_by_price or triggered_by_vix


def get_crash_summary(nasdaq_change_pct: float, vix: float | None = None) -> str:
    """Return a short plain-text summary of crash status and key rules."""
    active = is_crash(nasdaq_change_pct, vix)
    lines = [
        f"Crash Mode      : {'ACTIVE' if active else 'INACTIVE'}",
        f"NASDAQ Change   : {nasdaq_change_pct:+.2f}%",
    ]
    if vix is not None:
        lines.append(f"VIX             : {vix:.1f}")
    if active:
        lines += [
            f"Max Position    : {CRASH_RULES['max_position_size_pct']}%",
            f"Cash Reserve    : {CRASH_RULES['cash_reserve_pct']}%",
            f"New Longs       : {'YES' if CRASH_RULES['new_long_entries_allowed'] else 'NO'}",
            "Action          : Follow 10-step crash playbook",
        ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# QUICK SELF-TEST
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(get_crash_summary(nasdaq_change_pct=-4.7, vix=38))
    print()
    print(CRASH_PROMPT)
