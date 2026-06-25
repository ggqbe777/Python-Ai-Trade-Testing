"""
AI Stock Research Prompt
------------------------
A ready-to-use prompt template that instructs an AI model to research
and recommend stocks worth considering for investment.

Usage with the Anthropic SDK:
    pip install anthropic
    export ANTHROPIC_API_KEY=your_key_here
    python stock_research_prompt.py
"""

import os

# ---------- SETTINGS ----------
RISK_PROFILE = "moderate"        # "conservative", "moderate", or "aggressive"
INVESTMENT_HORIZON = "long-term" # "short-term" (< 1 yr), "mid-term" (1-3 yr), "long-term" (3+ yr)
SECTORS_OF_INTEREST = [          # Leave empty [] to research all sectors
    "technology",
    "healthcare",
    "clean energy",
]
MAX_STOCKS_TO_RETURN = 5
# ------------------------------


STOCK_RESEARCH_PROMPT = f"""
You are a professional equity research analyst with deep expertise in financial
markets, fundamental analysis, and macroeconomic trends.

Your task is to identify and evaluate stocks that represent strong investment
opportunities right now based on current market conditions, recent earnings,
sector momentum, and broader economic signals.

## Investor Profile
- Risk tolerance: {RISK_PROFILE}
- Investment horizon: {INVESTMENT_HORIZON}
- Sectors of interest: {", ".join(SECTORS_OF_INTEREST) if SECTORS_OF_INTEREST else "all sectors"}

## Research Instructions

1. **Market Context**: Briefly summarize the current macroeconomic environment
   (interest rates, inflation trends, sector rotations, geopolitical factors)
   that should influence stock selection today.

2. **Stock Screening**: Identify {MAX_STOCKS_TO_RETURN} stocks that match the
   investor profile above. For each stock, evaluate:
   - Recent price trend and momentum
   - Fundamental strength (revenue growth, earnings, margins, debt levels)
   - Valuation (P/E, P/S, EV/EBITDA relative to peers and historical averages)
   - Upcoming catalysts (earnings, product launches, regulatory decisions, etc.)
   - Key risks to the thesis

3. **Stock Recommendations**: For each recommended stock provide:
   - **Ticker**: Stock symbol
   - **Company**: Full company name
   - **Sector / Industry**: Classification
   - **Current Thesis**: 2-3 sentence investment case
   - **Bull Case**: What could make this significantly outperform
   - **Bear Case**: What could invalidate the thesis
   - **Key Metrics**: 3-4 most relevant financial metrics right now
   - **Time Horizon**: Suggested holding period
   - **Conviction Level**: High / Medium / Low with justification

4. **Portfolio Fit**: Explain how these picks work together — diversification,
   correlated risks, and suggested position sizing guidance.

5. **Disclaimer**: Always conclude with a standard investment disclaimer.

Begin your research now and present findings in a clear, structured report.
"""


def build_prompt(additional_context: str = "") -> str:
    """Return the full research prompt, optionally appending extra context."""
    prompt = STOCK_RESEARCH_PROMPT
    if additional_context.strip():
        prompt += f"\n\n## Additional Context from User\n{additional_context.strip()}"
    return prompt


def run_research(additional_context: str = "") -> None:
    """Send the prompt to Claude and stream the response to stdout."""
    try:
        import anthropic
    except ImportError:
        print("Anthropic SDK not installed. Run: pip install anthropic")
        return

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Set ANTHROPIC_API_KEY environment variable before running.")
        return

    client = anthropic.Anthropic(api_key=api_key)
    prompt = build_prompt(additional_context)

    print("=" * 60)
    print("AI STOCK RESEARCH REPORT")
    print("=" * 60)
    print(f"Risk Profile   : {RISK_PROFILE}")
    print(f"Horizon        : {INVESTMENT_HORIZON}")
    print(f"Sectors        : {', '.join(SECTORS_OF_INTEREST) or 'All'}")
    print("=" * 60 + "\n")

    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

    print("\n")


if __name__ == "__main__":
    extra = input(
        "Any additional context or constraints for the AI? "
        "(press Enter to skip): "
    ).strip()
    run_research(additional_context=extra)
