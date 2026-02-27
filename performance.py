import csv
from collections import defaultdict

file = "data/signal_history.csv"

rows = []

try:
    with open(file) as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
except FileNotFoundError:
    print("No signal history yet.")
    exit()

# group rows by ticker
by_ticker = defaultdict(list)
for r in rows:
    by_ticker[r["ticker"]].append(r)

print("\n=== Signal Performance Estimate ===\n")

for ticker, data in by_ticker.items():
    data.sort(key=lambda x: x["timestamp"])

    wins = 0
    losses = 0
    moves = []

    # compare each signal with the next recorded price
    for i in range(len(data) - 1):
        cur = data[i]
        nxt = data[i + 1]

        price_now = float(cur["price"])
        price_next = float(nxt["price"])
        signal = cur["signal"]

        move = (price_next - price_now) / price_now * 100
        moves.append(move)

        if signal == "BUY" and move > 0:
            wins += 1
        elif signal == "SELL" and move < 0:
            wins += 1
        elif signal != "NEUTRAL":
            losses += 1

    total = wins + losses
    winrate = (wins / total * 100) if total else 0
    avg_move = sum(moves) / len(moves) if moves else 0

    print(f"{ticker}")
    print(f"  Signals evaluated: {total}")
    print(f"  Win rate:          {winrate:.1f}%")
    print(f"  Avg move next day: {avg_move:.2f}%\n")
