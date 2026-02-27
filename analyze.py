import csv
from collections import defaultdict

file = "data/signal_history.csv"

stats = defaultdict(lambda: {
    "BUY": 0,
    "SELL": 0,
    "NEUTRAL": 0,
    "confidence_sum": 0,
    "count": 0
})

try:
    with open(file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            ticker = row["ticker"]
            signal = row["signal"]
            confidence = int(row["confidence"])

            stats[ticker][signal] += 1
            stats[ticker]["confidence_sum"] += confidence
            stats[ticker]["count"] += 1

except FileNotFoundError:
    print("No signal history yet. Run trader.py first.")
    exit()

print("\n=== Strategy Analysis Report ===\n")

for ticker, s in stats.items():
    avg_conf = s["confidence_sum"] / s["count"] if s["count"] else 0

    print(f"{ticker}")
    print(f"  BUY signals:     {s['BUY']}")
    print(f"  SELL signals:    {s['SELL']}")
    print(f"  NEUTRAL signals: {s['NEUTRAL']}")
    print(f"  Avg confidence:  {avg_conf:.1f}%")

    if s["BUY"] > s["SELL"]:
        bias = "Bullish"
    elif s["SELL"] > s["BUY"]:
        bias = "Bearish"
    else:
        bias = "Balanced"

    print(f"  Bias:            {bias}\n")
