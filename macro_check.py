import yfinance as yf
import pandas as pd
import sys

def get_series_safe(df, column):
    series = df[column]
    if isinstance(series, pd.DataFrame):
        series = series.iloc[:, 0]
    return series.astype(float)

def analyze_asset(ticker):
    print(f"\n===== {ticker} =====")

    data = yf.download(ticker, period="1y", interval="1d", progress=False)

    if data.empty:
        print("No data available")
        return

    close = get_series_safe(data, "Close")

    ma50 = close.rolling(50).mean()
    ma200 = close.rolling(200).mean()

    price = close.iloc[-1]
    ma50_now = ma50.iloc[-1]
    ma200_now = ma200.iloc[-1]
    ma200_prev = ma200.iloc[-20]

    print("Current Price:", round(price, 2))
    print("MA50:", round(ma50_now, 2))
    print("MA200:", round(ma200_now, 2))

    # Structure
    if price > ma200_now:
        print("Trend: ABOVE MA200 (Bullish Structure)")
    else:
        print("Trend: BELOW MA200 (Bearish Structure)")

    # Slope
    if ma200_now > ma200_prev:
        print("MA200 Slope: RISING")
    else:
        print("MA200 Slope: FALLING")

    # Momentum alignment
    if ma50_now > ma200_now:
        print("Momentum: STRONG (Golden Alignment)")
    else:
        print("Momentum: WEAKENING")

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python3 macro_check.py TICKER1 TICKER2 ...")
        sys.exit()

    tickers = [t.upper() for t in sys.argv[1:]]

    for ticker in tickers:
        analyze_asset(ticker)

    # Optional: always print USD + Yield macro context
    print("\n===== MACRO CONTEXT =====")
    analyze_asset("DX-Y.NYB")
    analyze_asset("^TNX")
