import yfinance as yf
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
from math import sqrt

INITIAL_CAPITAL = 50000
RISK_PER_TRADE = 0.01


def get_series_safe(df, column):
    series = df[column]
    if isinstance(series, pd.DataFrame):
        series = series.iloc[:, 0]
    return series.astype(float)


def backtest(ticker):

    data = yf.download(ticker, period="5y", interval="1d", progress=False)
    if data.empty:
        raise Exception("No data")

    close = get_series_safe(data, "Close")
    high = get_series_safe(data, "High")
    low = get_series_safe(data, "Low")

    ma200 = close.rolling(200).mean()
    rsi = RSIIndicator(close).rsi()
    atr = AverageTrueRange(high, low, close, window=14).average_true_range()

    capital = INITIAL_CAPITAL
    equity_curve = []
    trades = []
    position = None

    for i in range(200, len(close)):

        price = float(close.iloc[i])
        ma = ma200.iloc[i]
        r = rsi.iloc[i]
        a = atr.iloc[i]

        if pd.isna(ma) or pd.isna(r) or pd.isna(a):
            continue

        # ENTRY
        if position is None:
            if price > ma and 40 < r < 65:

                stop = price - (1.5 * a)
                target = price + (3 * a)

                risk_amount = capital * RISK_PER_TRADE
                size = risk_amount / (price - stop)

                position = {
                    "entry": price,
                    "stop": stop,
                    "target": target,
                    "size": size
                }

        # EXIT
        else:
            if price <= position["stop"]:
                loss = (position["entry"] - position["stop"]) * position["size"]
                capital -= loss
                trades.append(-1)
                position = None

            elif price >= position["target"]:
                profit = (position["target"] - position["entry"]) * position["size"]
                capital += profit
                trades.append(2)
                position = None

        equity_curve.append(capital)

    # ----- STATISTICS -----

    years = 5
    cagr = (capital / INITIAL_CAPITAL) ** (1 / years) - 1

    wins = [t for t in trades if t > 0]
    losses = [t for t in trades if t < 0]

    win_rate = len(wins) / len(trades) if trades else 0
    avg_win = np.mean(wins) if wins else 0
    avg_loss = abs(np.mean(losses)) if losses else 0

    expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)

    profit_factor = (sum(wins) / abs(sum(losses))) if losses else float('inf')

    # Longest losing streak
    max_streak = 0
    current_streak = 0
    for t in trades:
        if t < 0:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0

    # Sharpe ratio (daily)
    daily_returns = pd.Series(equity_curve).pct_change().dropna()
    sharpe = (daily_returns.mean() / daily_returns.std()) * sqrt(252) if daily_returns.std() != 0 else 0

    max_drawdown = (
        pd.Series(equity_curve)
        .div(pd.Series(equity_curve).cummax())
        .sub(1)
        .min()
    )

    return {
        "final_capital": round(capital, 2),
        "CAGR_%": round(cagr * 100, 2),
        "total_trades": len(trades),
        "win_rate_%": round(win_rate * 100, 2),
        "expectancy_R": round(expectancy, 3),
        "profit_factor": round(profit_factor, 2),
        "longest_losing_streak": max_streak,
        "Sharpe_ratio": round(sharpe, 2),
        "max_drawdown_%": round(max_drawdown * 100, 2)
    }


if __name__ == "__main__":
    ticker = "GLD"
    results = backtest(ticker)

    print("\nStatistical Backtest for", ticker)
    print("-------------------------------------")
    for k, v in results.items():
        print(f"{k}: {v}")
