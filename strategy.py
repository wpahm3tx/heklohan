import pandas as pd
import numpy as np

def indicators(df, ema_fast=9, ema_slow=21, rsi_period=14,
               macd_fast=12, macd_slow=26, macd_signal=9):
    d = df.copy()
    d["ema_fast"] = d["close"].ewm(span=ema_fast, adjust=False).mean()
    d["ema_slow"] = d["close"].ewm(span=ema_slow, adjust=False).mean()

    delta = d["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/rsi_period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/rsi_period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    d["rsi"] = 100 - (100 / (1 + rs))

    fast = d["close"].ewm(span=macd_fast, adjust=False).mean()
    slow = d["close"].ewm(span=macd_slow, adjust=False).mean()
    d["macd"] = fast - slow
    d["macd_signal"] = d["macd"].ewm(span=macd_signal, adjust=False).mean()
    return d.dropna()

def buy_signal(row):
    return (
        row["ema_fast"] > row["ema_slow"]
        and 50 <= row["rsi"] <= 70
        and row["macd"] > row["macd_signal"]
        and row["close"] > row["ema_fast"]
    )

def exit_signal(row):
    return row["ema_fast"] < row["ema_slow"]
