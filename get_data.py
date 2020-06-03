from keys import *
import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go #candlestick graph

from binance.client import Client
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
    df["Date"] = pd.to_datetime(df["Open time"], unit='ms').dt.datetime
    print(df)
    fig = go.Figure(data=[go.Candlestick(
                x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'])])
    fig.show(renderer='vscode')
