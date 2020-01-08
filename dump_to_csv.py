import pandas_datareader as web

with open("symbols.txt", "r") as f:
    stocks = [line.strip() for line in f]

data = web.DataReader(stocks, "yahoo", start="2000-1-1", end="2019-12-31")
data["Adj Close"].to_csv("prices.csv")
data["Volume"].to_csv("volume.csv")
