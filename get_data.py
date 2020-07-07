from keys import *

import requests
from binance.client import Client

from datetime import datetime, timedelta
import pandas as pd
import numpy as np

import plotly.graph_objects as go
import plotly.express as px

client = Client(api_key, api_secret)

def UTC_to_milliseconds(utc=None):
    """Converts a UTC string in the form %Y-%m-%dT%H:%M:%S to milliseconds since epoch 
    Returns:
        int: milliseconds since epoch
    """
    return int(datetime.strptime(utc, "%Y-%m-%d %H:%M:%S").timestamp()*1000)

def milliseconds_to_UTC(milliseconds=None):
    """Converts seconds since epoch to a string in the form %Y-%m-%dT%H:%M:%S

    Args:
        milliseconds (int, optional): milliseconds since epoch. Defaults to None.

    Returns:
        utc: datetime object
    """
    return datetime.utcfromtimestamp(milliseconds/1000)

def get_all_symbols():
    data = []
    for symbol in client.get_all_tickers():
        data.append(symbol["symbol"])
    return data

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
def get_kline_data(symbol, interval, start_date, end_date=None):
    """[summary]

    Args:
        symbol (str): Name of symbol pair e.g BNBBTC
        interval (str): Binance Kline interval
        start_date (str/int): Start date string in UTC format or timestamp in milliseconds
        end_date (str/int): Optional - end date string in UTC format or timestamp in milliseconds (default will fetch everything up to now)
    """
    column_names = ["Open time", "Open", "High", "Low", "Close", "Volume", "Close time", "Quote asset volume", "Number of trades", "Taker buy base asset volume", "Taker buy quote asset volume", "Ignore"]
    data = []
    count = 0
    for kline in client.get_historical_klines_generator(symbol, interval, start_date, end_date):
        count += 1
        if count % 1000 == 0:
            print(count)
        data.append(tuple(kline))

    #df = pd.DataFrame(data, columns=column_names)
    #df["Date"] = pd.to_datetime(df["Open time"], unit='ms')
    return data

#print(get_kline_data("BTCUSDT", client.KLINE_INTERVAL_1WEEK, UTC_to_milliseconds("2020-01-01 00:00:00"), UTC_to_milliseconds(str(datetime.now())[:-7])))


# Aggregate trade structure
# "a": 26129,         # Aggregate tradeId
# "p": "0.01633102",  # Price
# "q": "4.70443515",  # Quantity
# "f": 27781,         # First tradeId
# "l": 27781,         # Last tradeId
# "T": 1498793709153, # Timestamp
# "m": true,          # Was the buyer the maker?
# "M": true           # Was the trade the best price match?
def get_agg_data(symbol, start_date):
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
    return df

#print(get_agg_data("BTCUSDT", UTC_to_milliseconds("2020-06-16 12:00:00")))

def tradeID_at_date(symbol, date):
    """Given a datetime returns the tradeID for the date.

    Args:
        symbol (String): Name of symbol pair e.g BNBBTC
        date (datetime): datetime string in the form dd/mm/yyyy
    """
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
        #print(response[-1])
        return response[-1]['a']
    else:
        raise Exception('no trades found')

def get_historical_data(symbol, start_date, end_date=None):
    #! Depreciated, too much data to handle at the moment
    """Gets histroical trade data from a certain date up until the end date or if not given the current date.

    Args:
        symbol (str): Name of symbol pair e.g BNBBTC
        interval (str): Binance Kline interval
        start_date (str/int): Start date string in UTC format or timestamp in milliseconds
        end_date (str/int): Optional - end date string in UTC format or timestamp in milliseconds (default will fetch everything up to now)
    """
    start_id = tradeID_at_date(symbol, start_date)
    if end_date is None: end_date = int(datetime.now().timestamp()) * 1000
    data = []
    current_date = start_date
    while current_date < end_date:
        hist_trades = list(client.get_aggregate_trades(symbol=symbol, fromId = start_id))
        for trade in hist_trades:
            data.append(list(trade.values()))
        current_date = hist_trades[len(hist_trades)-1]["T"]
        start_id = hist_trades[len(hist_trades)-1]["a"]
        
    column_names = ["Agg tradeID", "Price", "Quantity", "First tradeID", "Last tradeID", "Timestamp", "Buyer Maker", "Price Match"]
    df = pd.DataFrame(data, columns=column_names)
    return df