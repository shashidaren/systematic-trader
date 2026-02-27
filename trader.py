import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
import requests


def get_indicators(ticker):
    data = yf.download(ticker, period="2y", interval="1d", progress=False)

    if data.empty:
        raise Exception("No market data returned.")

    close = data["Close"].squeeze()

    ma50 = close.rolling(50).mean()
    ma200 = close.rolling(200).mean()
    rsi = RSIIndicator(close).rsi()

    return {
        "price": float(close.iloc[-1]),
        "ma50": float(ma50.iloc[-1]) if pd.notna(ma50.iloc[-1]) else None,
        "ma200": float(ma200.iloc[-1]) if pd.notna(ma200.iloc[-1]) else None,
        "rsi": float(rsi.iloc[-1]) if pd.notna(rsi.iloc[-1]) else None,
        "series": close
    }


def get_news(ticker):
    url = f"https://news.google.com/rss/search?q={ticker}+stock"
    r = requests.get(url, timeout=10)

    titles = []
    parts = r.text.split("<title>")[2:7]

    for p in parts:
        titles.append(p.split("</title>")[0])

    return titles


def generate_signal(ind):
    score = 0
    max_score = 3
    reasons = []

    if ind["ma50"] is not None:
        if ind["price"] > ind["ma50"]:
            score += 1
            reasons.append("Price above MA50 (short-term bullish)")
        else:
            score -= 1
            reasons.append("Price below MA50 (short-term bearish)")

    if ind["ma200"] is not None:
        if ind["price"] > ind["ma200"]:
            score += 1
            reasons.append("Above MA200 (long-term bullish)")
        else:
            score -= 1
            reasons.append("Below MA200 (long-term bearish)")

    if ind["rsi"] is not None:
        if ind["rsi"] < 30:
            score += 1
            reasons.append("RSI oversold (bounce possible)")
        elif ind["rsi"] > 70:
            score -= 1
            reasons.append("RSI overbought (pullback risk)")
        else:
            reasons.append("RSI neutral")

    if score >= 2:
        signal = "BUY"
    elif score <= -2:
        signal = "SELL"
    else:
        signal = "NEUTRAL"

    confidence = int((abs(score) / max_score) * 100)

    return signal, confidence, reasons, score


def timing_hint(ind):
    hints = []
    price = ind["price"]
    ma50 = ind["ma50"]
    rsi = ind["rsi"]
    series = ind["series"]

    if ma50 is not None:
        distance = (price - ma50) / ma50

        if distance < -0.05:
            hints.append("Price far below MA50 → wait for rebound before entry")
        elif distance > 0.05:
            hints.append("Price extended above MA50 → avoid chasing, wait pullback")
        else:
            hints.append("Price near MA50 → breakout or rejection likely soon")

    if len(series) > 5:
        recent = series.iloc[-5:]
        if recent.iloc[-1] > recent.iloc[0]:
            hints.append("Short-term momentum improving")
        else:
            hints.append("Short-term momentum weakening")

    if rsi is not None:
        if rsi < 35:
            hints.append("RSI low → watch for bounce setup")
        elif rsi > 65:
            hints.append("RSI high → risk of pullback")

    return hints


def suggested_action(signal, hints):

    if signal == "BUY":
        for h in hints:
            if "extended" in h:
                return "Wait for pullback before entry"
            if "breakout" in h:
                return "Watch for breakout confirmation before entry"
        return "Look for buying opportunities on strength"

    if signal == "SELL":
        for h in hints:
            if "rebound" in h:
                return "Avoid shorting here, wait for weak bounce"
        return "Look for selling opportunities on weakness"

    return "No clear edge — wait for better setup"


def main():
    import sys
    from datetime import datetime
    import os

    if len(sys.argv) < 2:
        print("Usage: python trader.py TICKER")
        return

    ticker = sys.argv[1].upper()

    print(f"\nAnalyzing {ticker}...\n")

    indicators = get_indicators(ticker)
    news = get_news(ticker)
    signal, confidence, reasons, score = generate_signal(indicators)
    hints = timing_hint(indicators)
    action = suggested_action(signal, hints)

    # ✅ Logging
    os.makedirs("data", exist_ok=True)
    log_line = f"{datetime.utcnow().isoformat()} | {ticker} | {signal} | {confidence}% | {action}\n"
    with open("data/signals.log", "a") as f:
        f.write(log_line)

    print("Indicators:", {k:v for k,v in indicators.items() if k != "series"})
    print(f"\nMarket Bias: {signal} (Confidence: {confidence}%)")

    print("\nReasoning:")
    for r in reasons:
        print("-", r)

    print("\nTiming Hints:")
    for h in hints:
        print("-", h)

    print(f"\nSuggested Action: {action}")

    print("\nTop News:")
    for n in news:
        print("-", n)


if __name__ == "__main__":
    main()
