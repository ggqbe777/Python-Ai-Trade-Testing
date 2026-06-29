"""
ai_trade_controller.py
----------------------
Master AI Trade Controller
--------------------------
The single entry point for the entire AI trading system.
Automatically detects the market regime, selects the correct strategy
(DEFENSE, ATTACK, CONSERVE, or MIXED), builds the AI prompt, sends it
to Claude, and streams the trading recommendation back.

All other files in this project feed into this controller:
    trading_reference.py       — core rules and indicator guide
    nasdaq_crash_protocol.py   — crash-mode overrides
    strategy_defense.py        — capital preservation mode
    strategy_attack.py         — aggressive growth mode
    strategy_conserve.py       — income and wealth preservation mode
    strategy_mixed.py          — dynamic multi-mode (auto-selects allocation)

Run:
    pip install anthropic
    export ANTHROPIC_API_KEY=your_key_here
    python ai_trade_controller.py
"""

import os
from datetime import date

# ---------------------------------------------------------------------------
# IMPORT ALL STRATEGY MODULES
# ---------------------------------------------------------------------------
try:
    from trading_reference import build_trading_context, INDICATOR_GUIDE
    from nasdaq_crash_protocol import is_crash, CRASH_PROMPT, get_crash_summary
    from strategy_defense import DEFENSE_PROMPT, get_context as defense_context, check_entry
    from strategy_attack import ATTACK_PROMPT, get_context as attack_context, score_setup
    from strategy_conserve import CONSERVE_PROMPT, get_context as conserve_context, dividend_safety_score
    from strategy_mixed import MIXED_PROMPT, get_context as mixed_context, detect_regime, get_allocation
    MODULES_LOADED = True
except ImportError as e:
    MODULES_LOADED = False
    _IMPORT_ERROR = str(e)

# ---------------------------------------------------------------------------
# CONTROLLER SETTINGS
# ---------------------------------------------------------------------------
DEFAULT_MODEL       = "claude-opus-4-8"
DEFAULT_MAX_TOKENS  = 4096
AUTO_DETECT_REGIME  = True   # Let the controller pick the strategy automatically

# ---------------------------------------------------------------------------
# STRATEGY REGISTRY
# ---------------------------------------------------------------------------
STRATEGIES = {
    "DEFENSE":  "Capital preservation — defensive stocks, tight stops, 50% cash.",
    "ATTACK":   "Aggressive growth — momentum stocks, wide stops, pyramiding.",
    "CONSERVE": "Income focus — dividends, bonds, slow compounding.",
    "MIXED":    "Dynamic — auto-allocates across all three based on regime.",
    "CRASH":    "Crash mode — capital survival, inverse ETFs, 40%+ cash.",
}

# ---------------------------------------------------------------------------
# REGIME → STRATEGY MAP
# ---------------------------------------------------------------------------
REGIME_STRATEGY_MAP = {
    "BULL":    "ATTACK",
    "NEUTRAL": "MIXED",
    "BEAR":    "DEFENSE",
    "CRASH":   "CRASH",
}

# ---------------------------------------------------------------------------
# REGIME DETECTOR
# ---------------------------------------------------------------------------
def auto_detect_strategy(
    sp500_above_200sma: bool,
    vix: float,
    nasdaq_change_pct: float = 0.0,
    pct_stocks_above_50sma: float | None = None,
) -> str:
    """Detect market regime and return the recommended strategy name."""
    regime = detect_regime(sp500_above_200sma, vix, nasdaq_change_pct, pct_stocks_above_50sma)
    return REGIME_STRATEGY_MAP.get(regime, "MIXED"), regime


# ---------------------------------------------------------------------------
# PROMPT BUILDER — assembles the right context for the chosen strategy
# ---------------------------------------------------------------------------
def build_prompt(
    strategy: str,
    ticker: str | None = None,
    price: float | None = None,
    rsi: float | None = None,
    macd_signal: str | None = None,
    above_200sma: bool | None = None,
    sp500_above_200sma: bool | None = None,
    vix: float | None = None,
    nasdaq_change_pct: float | None = None,
    question: str = "",
) -> str:
    """
    Build the full AI prompt for the chosen strategy.
    Combines the strategy system prompt with live market data context.
    """
    strategy = strategy.upper()

    # Base strategy prompt
    if strategy == "DEFENSE":
        base = defense_context(question)
    elif strategy == "ATTACK":
        base = attack_context(question)
    elif strategy == "CONSERVE":
        base = conserve_context(question)
    elif strategy == "CRASH":
        base = CRASH_PROMPT + (f"\n\nUser question: {question}" if question else "")
    else:
        base = mixed_context(
            sp500_above_200sma=sp500_above_200sma,
            vix=vix,
            nasdaq_change_pct=nasdaq_change_pct,
            extra=question,
        )

    # Append live ticker context if provided
    if ticker and price:
        live = build_trading_context(
            ticker=ticker,
            price=price,
            rsi=rsi,
            macd_signal=macd_signal,
            above_200sma=above_200sma,
            market_regime=strategy,
            nasdaq_change_pct=nasdaq_change_pct,
            vix=vix,
        )
        base = base + "\n\n" + live

    return base


# ---------------------------------------------------------------------------
# AI CALL — streams Claude's response to stdout
# ---------------------------------------------------------------------------
def run_ai(prompt: str, model: str = DEFAULT_MODEL) -> None:
    """Send the prompt to Claude and stream the response."""
    try:
        import anthropic
    except ImportError:
        print("Anthropic SDK not installed. Run:  pip install anthropic")
        return

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Set ANTHROPIC_API_KEY environment variable before running.")
        return

    client = anthropic.Anthropic(api_key=api_key)

    with client.messages.stream(
        model=model,
        max_tokens=DEFAULT_MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
    print("\n")


# ---------------------------------------------------------------------------
# PRINT HEADER
# ---------------------------------------------------------------------------
def print_header(strategy: str, regime: str, ticker: str | None) -> None:
    width = 60
    print("=" * width)
    print("  AI TRADE CONTROLLER".center(width))
    print(f"  Date: {date.today().isoformat()}".center(width))
    print("=" * width)
    print(f"  Strategy   : {strategy}")
    print(f"  Regime     : {regime}")
    if ticker:
        print(f"  Ticker     : {ticker}")
    print("=" * width + "\n")


# ---------------------------------------------------------------------------
# INTERACTIVE CLI
# ---------------------------------------------------------------------------
def interactive_mode() -> None:
    """Step-by-step prompts to gather market data and run the AI."""

    print("\n" + "=" * 60)
    print("  AI TRADE CONTROLLER — Interactive Mode")
    print("=" * 60 + "\n")

    if not MODULES_LOADED:
        print(f"Warning: could not import all strategy modules ({_IMPORT_ERROR}).")
        print("Running in standalone mode with MIXED strategy only.\n")

    # --- Collect market conditions ---
    print("STEP 1: Market Conditions")
    sp500_str = input("  Is S&P 500 above its 200-day SMA? (y/n): ").strip().lower()
    sp500_above_200sma = sp500_str == "y"

    vix_str = input("  Current VIX level (e.g. 18.5): ").strip()
    vix = float(vix_str) if vix_str else 20.0

    ndq_str = input("  NASDAQ change today % (e.g. -1.2 or 0.8, Enter to skip): ").strip()
    nasdaq_change_pct = float(ndq_str) if ndq_str else 0.0

    # --- Auto-detect or manual strategy ---
    print("\nSTEP 2: Strategy Selection")
    print("  Available strategies:")
    for name, desc in STRATEGIES.items():
        print(f"    {name:<10} — {desc}")

    strategy_input = input(
        "\n  Type a strategy name (or press Enter to auto-detect): "
    ).strip().upper()

    if strategy_input in STRATEGIES:
        strategy = strategy_input
        regime = "MANUAL"
    else:
        strategy, regime = auto_detect_strategy(sp500_above_200sma, vix, nasdaq_change_pct)
        print(f"  Auto-detected regime: {regime} → using {strategy} strategy")

    # --- Optional ticker ---
    print("\nSTEP 3: Specific Stock (optional)")
    ticker = input("  Ticker to analyse (press Enter to skip): ").strip().upper() or None
    price, rsi, macd_signal, above_200sma = None, None, None, None

    if ticker:
        price_str = input(f"  Current price of {ticker}: $").strip()
        price = float(price_str) if price_str else None

        rsi_str = input(f"  RSI for {ticker} (press Enter to skip): ").strip()
        rsi = float(rsi_str) if rsi_str else None

        macd_str = input("  MACD signal (bullish/bearish/neutral, Enter to skip): ").strip().lower()
        macd_signal = macd_str if macd_str in ("bullish", "bearish", "neutral") else None

        sma_str = input(f"  Is {ticker} above its 200-day SMA? (y/n, Enter to skip): ").strip().lower()
        above_200sma = (sma_str == "y") if sma_str else None

    # --- User question ---
    print("\nSTEP 4: Your Question")
    question = input(
        "  What do you want the AI to analyse or recommend?\n  > "
    ).strip()

    # --- Build and run ---
    print_header(strategy, regime, ticker)

    prompt = build_prompt(
        strategy=strategy,
        ticker=ticker,
        price=price,
        rsi=rsi,
        macd_signal=macd_signal,
        above_200sma=above_200sma,
        sp500_above_200sma=sp500_above_200sma,
        vix=vix,
        nasdaq_change_pct=nasdaq_change_pct,
        question=question,
    )

    run_ai(prompt)


# ---------------------------------------------------------------------------
# PROGRAMMATIC API — use this when calling from another script
# ---------------------------------------------------------------------------
def analyse(
    question: str,
    strategy: str = "auto",
    ticker: str | None = None,
    price: float | None = None,
    rsi: float | None = None,
    macd_signal: str | None = None,
    above_200sma: bool | None = None,
    sp500_above_200sma: bool = True,
    vix: float = 20.0,
    nasdaq_change_pct: float = 0.0,
    silent_header: bool = False,
) -> None:
    """
    Programmatic entry point. Import and call this from any other script.

    Example:
        from ai_trade_controller import analyse
        analyse(
            question="Should I buy NVDA today?",
            ticker="NVDA",
            price=875.0,
            rsi=62,
            sp500_above_200sma=True,
            vix=17.0,
        )
    """
    if strategy.upper() == "AUTO" or strategy.upper() not in STRATEGIES:
        chosen_strategy, regime = auto_detect_strategy(
            sp500_above_200sma, vix, nasdaq_change_pct
        )
    else:
        chosen_strategy = strategy.upper()
        regime = "MANUAL"

    if not silent_header:
        print_header(chosen_strategy, regime, ticker)

    prompt = build_prompt(
        strategy=chosen_strategy,
        ticker=ticker,
        price=price,
        rsi=rsi,
        macd_signal=macd_signal,
        above_200sma=above_200sma,
        sp500_above_200sma=sp500_above_200sma,
        vix=vix,
        nasdaq_change_pct=nasdaq_change_pct,
        question=question,
    )

    run_ai(prompt)


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    interactive_mode()
