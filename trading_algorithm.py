"""
Simple Moving Average Crossover Trading Algorithm
--------------------------------------------------
A beginner-friendly example that:
  1. Downloads historical stock data
  2. Calculates two moving averages (short + long)
  3. Generates buy/sell signals when they cross
  4. Backtests the strategy vs. just holding the stock
  5. Plots the results

Run this in VS Code after installing the required packages:
    pip install yfinance pandas matplotlib
"""

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt


# ---------- SETTINGS (change these to experiment) ----------
TICKER = "AAPL"          # Stock symbol (try "TSLA", "MSFT", "NVDA", etc.)
START_DATE = "2020-01-01"
END_DATE = "2025-01-01"
SHORT_WINDOW = 50        # Short-term moving average (days)
LONG_WINDOW = 200        # Long-term moving average (days)
STARTING_CASH = 10_000   # Pretend we start with $10,000
# -----------------------------------------------------------


def download_data(ticker, start, end):
    """Download historical price data from Yahoo Finance."""
    print(f"Downloading {ticker} data from {start} to {end}...")
    data = yf.download(ticker, start=start, end=end, auto_adjust=True)

    # yfinance sometimes returns multi-level columns — flatten them
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    if data.empty:
        raise ValueError("No data downloaded. Check ticker symbol or dates.")
    return data


def add_signals(data, short_window, long_window):
    """Add moving averages and buy/sell signals to the dataframe."""
    data["SMA_Short"] = data["Close"].rolling(window=short_window).mean()
    data["SMA_Long"] = data["Close"].rolling(window=long_window).mean()

    # Signal: 1 = we want to be holding the stock, 0 = sit in cash
    data["Signal"] = 0
    data.loc[data["SMA_Short"] > data["SMA_Long"], "Signal"] = 1

    # Position change: +1 = BUY today, -1 = SELL today, 0 = hold
    data["Position"] = data["Signal"].diff()
    return data


def backtest(data, starting_cash):
    """Simulate the strategy and compare it to buy-and-hold."""
    # Daily % returns of the stock
    data["Daily_Return"] = data["Close"].pct_change()

    # Strategy return = stock return ONLY on days we hold (shifted by 1
    # because we act on yesterday's signal at today's open)
    data["Strategy_Return"] = data["Daily_Return"] * data["Signal"].shift(1)

    # Cumulative growth of $1 invested
    data["Buy_Hold_Equity"] = (1 + data["Daily_Return"]).cumprod() * starting_cash
    data["Strategy_Equity"] = (1 + data["Strategy_Return"]).cumprod() * starting_cash
    return data


def print_summary(data, ticker):
    """Print a quick performance summary."""
    final_bh = data["Buy_Hold_Equity"].iloc[-1]
    final_strat = data["Strategy_Equity"].iloc[-1]
    buys = (data["Position"] == 1).sum()
    sells = (data["Position"] == -1).sum()

    print("\n" + "=" * 50)
    print(f"RESULTS for {ticker}")
    print("=" * 50)
    print(f"Starting cash:        ${STARTING_CASH:,.2f}")
    print(f"Buy & Hold final:     ${final_bh:,.2f}  "
          f"({(final_bh/STARTING_CASH - 1)*100:+.2f}%)")
    print(f"Strategy final:       ${final_strat:,.2f}  "
          f"({(final_strat/STARTING_CASH - 1)*100:+.2f}%)")
    print(f"Total BUY signals:    {buys}")
    print(f"Total SELL signals:   {sells}")
    print("=" * 50 + "\n")


def plot_results(data, ticker):
    """Show two charts: price+signals and equity curves."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # --- Top chart: price + moving averages + buy/sell markers ---
    ax1.plot(data.index, data["Close"], label="Close Price", alpha=0.6)
    ax1.plot(data.index, data["SMA_Short"],
             label=f"{SHORT_WINDOW}-day SMA", linewidth=1.2)
    ax1.plot(data.index, data["SMA_Long"],
             label=f"{LONG_WINDOW}-day SMA", linewidth=1.2)

    buys = data[data["Position"] == 1]
    sells = data[data["Position"] == -1]
    ax1.scatter(buys.index, buys["Close"], marker="^",
                color="green", s=100, label="BUY", zorder=5)
    ax1.scatter(sells.index, sells["Close"], marker="v",
                color="red", s=100, label="SELL", zorder=5)
    ax1.set_title(f"{ticker} — Moving Average Crossover Strategy")
    ax1.set_ylabel("Price (USD)")
    ax1.legend(loc="upper left")
    ax1.grid(alpha=0.3)

    # --- Bottom chart: strategy vs. buy-and-hold equity curves ---
    ax2.plot(data.index, data["Buy_Hold_Equity"],
             label="Buy & Hold", linewidth=1.5)
    ax2.plot(data.index, data["Strategy_Equity"],
             label="Strategy", linewidth=1.5)
    ax2.set_title("Portfolio Value Over Time")
    ax2.set_ylabel("Portfolio Value (USD)")
    ax2.set_xlabel("Date")
    ax2.legend(loc="upper left")
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.show()


def main():
    data = download_data(TICKER, START_DATE, END_DATE)
    data = add_signals(data, SHORT_WINDOW, LONG_WINDOW)
    data = backtest(data, STARTING_CASH)
    print_summary(data, TICKER)
    plot_results(data, TICKER)


if __name__ == "__main__":
    main()
