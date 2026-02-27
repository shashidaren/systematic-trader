import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
import requests
import csv
import os
from datetime import datetime
import sys

def get_indicators(ticker):
data = yf.download(ticker, period="2y", interval="1d", progress=False)

```
if data.empty:
    raise Exception(f"No market data for {ticker}")

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
```

def generate_signal(ind):
score = 0
reasons = []

```
if ind["ma50"] is not None:
    if ind["price"] > ind["ma50"]:
        score += 1
        reasons.append("Above MA50")
    else:
        score -= 1
        reasons.append("Below MA50")

if ind["ma200"] is not None:
    if ind["price"] > ind["ma200"]:
        score += 1
        reasons.append("Above MA200")
    else:
        score -= 1
        reasons.append("Below MA200")

if ind["rsi"] is not None:
    if ind["rsi"] < 30:
        score += 1
        reasons.append("RSI oversold")
    elif ind["rsi"] > 70:
        score -= 1
        reasons.append("RSI o
```

