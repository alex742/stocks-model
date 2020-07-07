from keys import *
from get_data import *

import sqlite3
from datetime import datetime, timedelta
import time
from binance.client import Client

client = Client(api_key, api_secret)


def build_db(symbols):
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    for symbol in symbols:
        try:
            c.execute("CREATE TABLE IF NOT EXISTS '{}' (Open_time DATETIME PRIMARY KEY, Open FLOAT, High FLOAT, Low FLOAT, Close FLOAT, Volume FLOAT, Close_time DATETIME, Quote_asset_volume FLOAT, Number_of_trades INT, Taker_buy_base_asset_volume FLOAT, Taker_buy_quote_asset_volume_FLOAT, Ignore INT)".format(symbol))
        except Exception as e:
            print("Error creating table for", symbol,e)
        print(symbol)
    conn.commit()
    conn.close()

def insert_data(db, symbols, interval, start_date, end_date=None):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    for symbol in symbols:
        start_time = time.time()
        data = get_kline_data(symbol, interval, start_date, end_date)
        for row in data:
            try:
                c.execute("insert into '{}' values (?,?,?,?,?,?,?,?,?,?,?,?)".format(symbol), row)
            except Exception as e:
                print("Error Inserting", symbol, "Err:", e)
        end_time = time.time()
        print("Inserted", symbol, "took", round(end_time - start_time, 2),"seconds.")
    conn.commit()
    conn.close()

def drop_tables(db, symbols):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    for symbol in symbols:
        start_time = time.time()
        try:
            c.execute("drop table '{}'".format(symbol))
        except Exception as e:
            print("Error Inserting", symbol, "Err:", e)
        end_time = time.time()
        print("Dropped table", symbol, "took", round(end_time - start_time, 2),"seconds.")
    conn.commit()
    conn.close()

#print(get_all_symbols())
#drop_tables(database_path, get_all_symbols())
#print(len(get_all_symbols()))
#build_db(["BTCUSDT", "ETHUSDT", "BCHUSDT", "LTCUSDT", "XRPUSDT"])
#insert_data(database_path, ["BTCUSDT", "ETHUSDT", "BCHUSDT", "LTCUSDT", "XRPUSDT"], client.KLINE_INTERVAL_1MINUTE, UTC_to_milliseconds("2019-01-01 00:00:00"), UTC_to_milliseconds("2020-01-01 00:00:00"))