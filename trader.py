import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
import requests
import csv
import os
from datetime import datetime
import sys

# ---------- MARKET DATA ----------

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

# ---------- SIGNAL ENGINE ----------

def generate_signal(ind):
score = 0

```
if ind["ma50"] is not None:
    score += 1 if ind["price"] > ind["ma50"] else -1

if ind["ma200"] is not None:
    score += 1 if ind["price"] > ind["ma200"] else -1

if ind["rsi"] is not None:
    if ind["rsi"] < 30:
        score += 1
    elif ind["rsi"] > 70:
        score -= 1

if score >= 2:
    signal = "BUY"
elif score <= -2:
    signal = "SELL"
else:
    signal = "NEUTRAL"

confidence = int(abs(score) / 3 * 100)
return signal, confidence
```

# ---------- CSV HISTORY ----------

def write_csv(timestamp, ticker, ind, signal, confidence):
os.makedirs("data", exist_ok=True)
file = "data/signal_history.csv"

```
new_file = not os.path.exists(file)

with open(file, "a", newline="") as f:
    writer = csv.writer(f)

    if new_file:
        writer.writerow([
            "timestamp","ticker","price","ma50","ma200","rsi","signal","confidence"
        ])

    writer.writerow([
        timestamp,
        ticker,
        ind["price"],
        ind["ma50"],
        ind["ma200"],
        ind["rsi"],
        signal,
        confidence
    ])
```

# ---------- SIGNAL CHANGE TRACKING ----------

def check_signal_change(ticker, new_signal):
file = "data/last_signals.csv"
os.makedirs("data", exist_ok=True)

```
last = {}

if os.path.exists(file):
    with open(file) as f:
        for row in csv.reader(f):
            if len(row) == 2:
                last[row[0]] = row[1]

changed = ticker not in last or last[ticker] != new_signal
last[ticker] = new_signal

with open(file, "w", newline="") as f:
    writer = csv.writer(f)
    for k, v in last.items():
        writer.writerow([k, v])

return changed
```

# ---------- TELEGRAM ALERT ----------

def send_telegram(msg):
token = os.environ.get("TELEGRAM_TOKEN")
chat = os.environ.get("TELEGRAM_CHAT")

```
if not token or not chat:
    return

url = f"https://api.telegram.org/bot{token}/sendMessage"
try:
    requests.post(url, json={"chat_id": chat, "text": msg}, timeout=10)
except Exception:
    pass
```

# ---------- SUMMARY OUTPUT ----------

def print_summary(results):
if not results:
return

```
print("\n=== Daily Signal Summary ===")

results.sort(key=lambda x: x["confidence"], reverse=True)

for r in results:
    print(f"{r['ticker']:10}  {r['signal']:7}  {r['confidence']:3}%   price={r['price']:.4f}")

strongest = results[0]
print("\nTop signal today:")
print(f"{strongest['ticker']} → {strongest['signal']} ({strongest['confidence']}%)")
```

# ---------- MAIN ----------

def main():
if len(sys.argv) < 2:
print("Usage: python trader.py TICKER1 TICKER2 ...")
return

```
tickers = [t.upper() for t in sys.argv[1:]]
timestamp = datetime.utcnow().isoformat()

results = []

for ticker in tickers:
    print(f"\nAnalyzing {ticker}...")

    try:
        ind = get_indicators(ticker)
        signal, confidence = generate_signal(ind)

        write_csv(timestamp, ticker, ind, signal, confidence)

        changed = check_signal_change(ticker, signal)

        print(f"Signal: {signal} ({confidence}%)  Price: {ind['price']}")

        if changed:
            msg = f"⚠ Signal change for {ticker}: {signal} ({confidence}%)"
            print(msg)
            send_telegram(msg)

        results.append({
            "ticker": ticker,
            "signal": signal,
            "confidence": confidence,
            "price": ind["price"]
        })

    except Exception as e:
        print("Error:", e)

print_summary(results)
```

if **name** == "**main**":
main()

