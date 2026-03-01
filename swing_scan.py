import yfinance as yf
import pandas as pd
import numpy as np
import sys
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

def get_series_safe(df, column):
    series = df[column]
    if isinstance(series, pd.DataFrame):
        series = series.iloc[:, 0]
    return series.astype(float)

def analyze_swing(ticker):
    print(f"\n===== SWING ANALYSIS: {ticker} =====")

    data = yf.download(ticker, period="1y", interval="1d", progress=False)

    if data.empty:
        print("No data")
        return

    close = get_series_safe(data, "Close")
    high = get_series_safe(data, "High")
    low = get_series_safe(data, "Low")

    ma50 = close.rolling(50).mean()
    ma200 = close.rolling(200).mean()
    rsi = RSIIndicator(close).rsi()
    atr = AverageTrueRange(high, low, close, window=14).average_true_range()

    price = close.iloc[-1]
    ma50_now = ma50.iloc[-1]
    ma200_now = ma200.iloc[-1]
    rsi_now = rsi.iloc[-1]
    atr_now = atr.iloc[-1]

    atr_pct = (atr_now / price) * 100
    atr_avg = atr.rolling(60).mean().iloc[-1]

    # Trend
    trend = "UP" if price > ma200_now else "DOWN"

    # Pullback condition
    pullback = price < ma50_now and price > ma200_now

    # RSI reset
    rsi_reset = 40 <= rsi_now <= 55

    # Volatility compression
    compression = atr_now < atr_avg

    # Breakout proximity
    high20 = close.rolling(20).max().iloc[-1]
    breakout_zone = price >= 0.98 * high20

    print("Trend:", trend)
    print("Price:", round(price, 2))
    print("RSI:", round(rsi_now, 2))
    print("ATR%:", round(atr_pct, 2))

    print("\nConditions:")
    print("Pullback Inside Uptrend:", pullback)
    print("RSI Reset Zone:", rsi_reset)
    print("Volatility Compression:", compression)
    print("Near 20-Day High:", breakout_zone)

    # Simple swing classification
    if trend == "UP" and pullback and rsi_reset:
        print("\nSwing Bias: Pullback Setup (Constructive)")
    elif trend == "UP" and breakout_zone:
        print("\nSwing Bias: Breakout Momentum Setup")
    elif trend == "DOWN":
        print("\nSwing Bias: Avoid Long Swings (Bearish Structure)")
    else:
        print("\nSwing Bias: Neutral / No Clear Setup")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 swing_scan.py TICKER")
        sys.exit()

    analyze_swing(sys.argv[1].upper())
