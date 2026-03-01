import yfinance as yf
import pandas as pd

ticker = "GLD"

data = yf.download(ticker, period="1y", interval="1d", progress=False)

close = data["Close"].squeeze()
ma200 = close.rolling(200).mean()

current_price = close.iloc[-1]
current_ma200 = ma200.iloc[-1]

print("Current Price:", round(current_price, 2))
print("MA200:", round(current_ma200, 2))

if current_price > current_ma200:
    print("Status: ABOVE MA200 (Uptrend intact)")
else:
    print("Status: BELOW MA200 (Trend broken)")
