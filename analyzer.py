import pandas as pd
import numpy as np
import datetime as dt
import math
import warnings

warnings.filterwarnings("ignore")

prices = pd.read_csv("prices.csv", index_col="Date", parse_dates=True)
volumechanges = pd.read_csv("volume.csv", index_col="Date", parse_dates=True).pct_change() * 100

today =  dt.date(2000, 1, 15)
simend = dt.date(2019, 12, 31)
with open("symbols.txt", "r") as f:
    tickers = [line.strip() for line in f]

transactionid = 0
money = 1000000
portfolio = {}
activelog = []
transactionlog = []

def getprice(date, ticker):
    global prices
    return prices.loc[date][ticker]


def transaction(id_, ticker, amount, price, type_, info):
    global transactionid
    data = {
        "ticker": ticker, "amount": amount, "price": price, "date": today,
        "type": type_,  "info": info
    }
    if type_ == "buy":
        exp_date = today + dt.timedelta(days=14)
        transactionid += 1
        data["id"] = transactionid
        data["exp_date"] = exp_date
        activelog.append(data)
    else:
        exp_date = today
        data["id"] = id_
        data["exp_date"] = exp_date
    transactionlog.append(data)


def buy(interestlst, allocated_money):
    global money, portfolio
    for item in interestlst:
        price = getprice(today, item)
        if np.isnan(price):
            return
        quantity = int(allocated_money // price)
        money -= quantity * price
        portfolio[item] += quantity
        transaction(0, item, quantity, price, "buy", "")  # 0 is like a dummy


def sell():  # Can be optimised further
    global money, portfolio, prices, today
    itemstoremove = []
    for i, log in enumerate(activelog):
        if log["exp_date"] <= today and log["type"] == "buy":  # 'and' Redundant?
            tickprice = getprice(today, log["ticker"])
            if np.isnan(tickprice):
                log["exp_date"] += dt.timedelta(days=1)
                continue
            money += log["amount"] * tickprice
            portfolio[log["ticker"]] -= log["amount"]
            transaction(
                log["id"], log["ticker"], log["amount"], tickprice,
                "sell", log["info"]
            )
            itemstoremove.append(i)

    itemstoremove.reverse()
    for elem in itemstoremove:
        activelog.remove(activelog[elem])


def simulation():
    global today, volumechanges, money
    start_date = today - dt.timedelta(days=14)
    series = volumechanges.loc[start_date:today].mean()
    interestlst = series[series > 100].index.tolist()
    sell()
    if interestlst:
        money_to_allocate = money / (2*len(interestlst))
        buy(interestlst, money_to_allocate)


def tradingday():  # Can be optimized
    global prices, today
    return np.datetime64(today) in list(prices.index.values)


def currentvalue():
    global money, portfolio, today, prices
    value = money
    for ticker in tickers:
        tickprice = getprice(today, ticker)
        if not np.isnan(tickprice):
            value += portfolio[ticker] * tickprice
    return round(value, 2)


def main():
    global portfolio, today
    portfolio = {ticker: 0 for ticker in tickers}
    while today < simend:
        while not tradingday():
            today += dt.timedelta(days=1)
        simulation()
        print(currentvalue(), round(money, 2), today)
        today += dt.timedelta(days=7)

if __name__ == "__main__":
    main()
