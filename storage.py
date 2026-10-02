import sqlite3
from datetime import datetime, timezone

class Store:
    def __init__(self, path="bot.db"):
        self.db = sqlite3.connect(path)
        self.db.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            symbol TEXT,
            side TEXT,
            price REAL,
            amount REAL,
            pnl REAL,
            mode TEXT
        )
        """)
        self.db.commit()

    def trade(self, symbol, side, price, amount, pnl=0.0, mode="paper"):
        self.db.execute(
            "INSERT INTO trades(time,symbol,side,price,amount,pnl,mode) VALUES(?,?,?,?,?,?,?)",
            (datetime.now(timezone.utc).isoformat(),
             symbol, side, price, amount, pnl, mode)
        )
        self.db.commit()
