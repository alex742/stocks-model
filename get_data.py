from keys import *

import requests
from binance.client import Client

from datetime import datetime, timedelta
import pandas as pd
import numpy as np

import plotly.graph_objects as go
import plotly.express as px

client = Client(api_key, api_secret)


#     Kline structure
#     1499040000000,      // Open time
#     "0.01634790",       // Open
#     "0.80000000",       // High
#     "0.01575800",       // Low
#     "0.01577100",       // Close
#     "148976.11427815",  // Volume
#     1499644799999,      // Close time
#     "2434.19055334",    // Quote asset volume
#     308,                // Number of trades
#     "1756.87402397",    // Taker buy base asset volume
#     "28.46694368",      // Taker buy quote asset volume
#     "17928899.62484339" // Ignore
def kline_plot(symbol, interval, start_date, end_date=None):
    """[summary]

    Args:
        symbol (str): Name of symbol pair e.g BNBBTC
        interval (str): Binance Kline interval
        start_date (str/int): Start date string in UTC format or timestamp in milliseconds
        end_date (str/int): Optional - end date string in UTC format or timestamp in milliseconds (default will fetch everything up to now)
    """
    column_names = ["Open time", "Open", "High", "Low", "Close", "Volume", "Close time", "Quote asset volume", "Number of trades", "Taker buy base asset volume", "Taker buy quote asset volume", "Ignore"]
    data = []
    for kline in client.get_historical_klines_generator(symbol, interval, start_date, end_date):
        data.append(kline)

    df = pd.DataFrame(data, columns=column_names)
    df["Date"] = pd.to_datetime(df["Open time"], unit='ms')#.dt.datetime
    #print(df)
    fig = go.Figure(data=[go.Candlestick(
                x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'])])
    fig.show(renderer='vscode')

# Aggregate trade structure
# "a": 26129,         # Aggregate tradeId
# "p": "0.01633102",  # Price
# "q": "4.70443515",  # Quantity
# "f": 27781,         # First tradeId
# "l": 27781,         # Last tradeId
# "T": 1498793709153, # Timestamp
# "m": true,          # Was the buyer the maker?
# "M": true           # Was the trade the best price match?
def agg_trade_plot(symbol, start_date):
    """Generates a scatter (line if dense enough) plot of the average price of trades since the start date.

    Args:
        symbol (String): Name of symbol pair e.g BNBBTC
        start_date (str/int): Start date string in UTC format or timestamp in milliseconds
    """
    column_names = ["Agg tradeID", "Price", "Quantity", "First tradeID", "Last tradeID", "Timestamp", "Buyer Maker", "Price Match"]
    data = []
    for trade in list(client.aggregate_trade_iter(symbol, start_str=start_date)):
        data.append(list(trade.values()))
    df = pd.DataFrame(data, columns=column_names)
    df["Date"] = pd.to_datetime(df["Timestamp"], unit='ms')
    fig = px.scatter(df[["Date","Price"]],
                x='Date',
                y='Price',
                color=df["Price Match"])
    fig.show(renderer='vscode')

def tradeID_at_date(symbol, date):
    """Given a datetime returns the tradeID for the date.

    Args:
        symbol (String): Name of symbol pair e.g BNBBTC
        date (datetime): datetime string in the form dd/mm/yyyy
    """
    date = int(datetime.strptime(date, '%d/%m/%Y').timestamp())
    start_date = date * 1000 #ms conversion
    end_date = (date + 60*59) * 1000 #ms conversion
    r = requests.get('https://api.binance.com/api/v3/aggTrades',
            params = {
                "symbol" : symbol,
                "startTime": start_date,
                "endTime": end_date
        })
    response = r.json()
    if len(response) > 0:
        return response[0]['a']
    else:
        raise Exception('no trades found')

print(tradeID_at_date("BTCUSDT", "08/06/2020"))