from create_database import *

def database_data():
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    rows = c.execute("SELECT * FROM BTCUSDT")
    for row in rows:
        print(row)


print(database_data())