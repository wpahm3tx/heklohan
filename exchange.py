import ccxt
import pandas as pd

class Exchange:
    def __init__(self, exchange_id, api_key="", api_secret=""):
        cls = getattr(ccxt, exchange_id)
        self.client = cls({
            "apiKey": api_key,
            "secret": api_secret,
            "enableRateLimit": True,
            "options": {"defaultType": "spot"},
        })
        self.client.load_markets()

    def candles(self, symbol, timeframe="15m", limit=250):
        rows = self.client.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(rows, columns=[
            "timestamp","open","high","low","close","volume"
        ])
        df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        return df

    def last_price(self, symbol):
        return float(self.client.fetch_ticker(symbol)["last"])

    def market_order(self, symbol, side, amount):
        return self.client.create_order(symbol, "market", side, amount)
