from create_database import *
import get_data as gd

def get_database_data(symbol, start_date, end_date):
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    rows = c.execute(f"SELECT Open_time, Open FROM {symbol} where (Open_time >= '{start_date}' AND Open_time < '{end_date}')")
    data = []
    for row in rows:
        data.append(row)
    return data

print(get_database_data("BTCUSDT","1577836800000", "1577840400000"))