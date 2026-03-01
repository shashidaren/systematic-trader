import yfinance as yf
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator

def get_series_safe(df, column):
    series = df[column]
    if isinstance(series, pd.DataFrame):
        series = series.iloc[:, 0]
    return series.astype(float)

def breakout_study(ticker):

    print(f"\n===== Breakout Research: {ticker} =====")

    data = yf.download(ticker, period="5y", interval="1d", progress=False)

    close = get_series_safe(data, "Close")

    ma200 = close.rolling(200).mean()
    rsi = RSIIndicator(close).rsi()
    high20 = close.rolling(20).max()

    df = pd.DataFrame({
        "close": close,
        "ma200": ma200,
        "rsi": rsi,
        "high20": high20
    })

    # Breakout condition
    df["breakout"] = (
        (df["close"] > df["ma200"]) &
        (df["rsi"] > 60) &
        (df["close"] >= 0.98 * df["high20"])
    )

    # Forward returns
    df["fwd_5"] = df["close"].shift(-5) / df["close"] - 1
    df["fwd_10"] = df["close"].shift(-10) / df["close"] - 1
    df["fwd_20"] = df["close"].shift(-20) / df["close"] - 1

    signals = df[df["breakout"]]

    print("Total Breakout Signals:", len(signals))

    if len(signals) == 0:
        print("No signals found.")
        return

    print("\nAverage Forward Returns:")
    print("5-Day :", round(signals["fwd_5"].mean() * 100, 2), "%")
    print("10-Day:", round(signals["fwd_10"].mean() * 100, 2), "%")
    print("20-Day:", round(signals["fwd_20"].mean() * 100, 2), "%")

    print("\nWin Rates:")
    print("5-Day :", round((signals["fwd_5"] > 0).mean() * 100, 2), "%")
    print("10-Day:", round((signals["fwd_10"] > 0).mean() * 100, 2), "%")
    print("20-Day:", round((signals["fwd_20"] > 0).mean() * 100, 2), "%")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 breakout_research.py TICKER")
        sys.exit()

    ticker = sys.argv[1].upper()
    breakout_study(ticker)
