import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

INITIAL_CAPITAL = 50000
RISK_PER_TRADE = 0.01  # 1% risk


def get_series_safe(df, column):
    """
    Safely extract a 1D pandas Series from yfinance output
    (handles 2D DataFrame columns issue)
    """
    series = df[column]
    if isinstance(series, pd.DataFrame):
        series = series.iloc[:, 0]
    return series.astype(float)


def backtest(ticker):

    data = yf.download(ticker, period="5y", interval="1d", progress=False)

    if data.empty:
        raise Exception("No data returned")

    # Extract clean 1D series
    close = get_series_safe(data, "Close")
    high = get_series_safe(data, "High")
    low = get_series_safe(data, "Low")

    # Compute indicators
    ma200 = close.rolling(200).mean()
    rsi = RSIIndicator(close).rsi()
    atr = AverageTrueRange(high, low, close, window=14).average_true_range()

    capital = INITIAL_CAPITAL
    peak = INITIAL_CAPITAL
    max_drawdown = 0

    position = None
    trades = []

    for i in range(200, len(close)):

        price = float(close.iloc[i])
        ma200_val = float(ma200.iloc[i]) if not pd.isna(ma200.iloc[i]) else None
        rsi_val = float(rsi.iloc[i]) if not pd.isna(rsi.iloc[i]) else None
        atr_val = float(atr.iloc[i]) if not pd.isna(atr.iloc[i]) else None

        if ma200_val is None or rsi_val is None or atr_val is None:
            continue

        # Update drawdown
        if capital > peak:
            peak = capital

        drawdown = (peak - capital) / peak
        max_drawdown = max(max_drawdown, drawdown)

        # ENTRY
        if position is None:
            if price > ma200_val and 40 < rsi_val < 65:

                stop = price - (1.5 * atr_val)
                target = price + (3 * atr_val)

                risk_amount = capital * RISK_PER_TRADE
                position_size = risk_amount / (price - stop)

                position = {
                    "entry": price,
                    "stop": stop,
                    "target": target,
                    "size": position_size
                }

        # EXIT
        else:
            if price <= position["stop"]:
                loss = (position["entry"] - position["stop"]) * position["size"]
                capital -= loss
                trades.append(-1)  # -1R
                position = None

            elif price >= position["target"]:
                profit = (position["target"] - position["entry"]) * position["size"]
                capital += profit
                trades.append(2)  # +2R
                position = None

    total_return = (capital - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
    win_rate = (trades.count(2) / len(trades) * 100) if trades else 0

    return {
        "final_capital": round(capital, 2),
        "return_%": round(total_return, 2),
        "trades": len(trades),
        "win_rate_%": round(win_rate, 2),
        "max_drawdown_%": round(max_drawdown * 100, 2)
    }


if __name__ == "__main__":
    ticker = "AAPL"  # Change to test others
    results = backtest(ticker)

    print("\nBacktest Results for", ticker)
    print("-----------------------------------")
    for k, v in results.items():
        print(f"{k}: {v}")
