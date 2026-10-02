import os
import pandas as pd
from dotenv import load_dotenv
from exchange import Exchange
from strategy import indicators, buy_signal, exit_signal

load_dotenv()

exchange = Exchange(os.getenv("EXCHANGE","binance"))
symbol = os.getenv("BACKTEST_SYMBOL","BTC/USDT")
timeframe = os.getenv("TIMEFRAME","15m")
balance = float(os.getenv("STARTING_BALANCE","1000"))
fee = float(os.getenv("FEE_PCT","0.001"))
sl = float(os.getenv("STOP_LOSS_PCT","0.015"))
tp = float(os.getenv("TAKE_PROFIT_PCT","0.03"))
risk = float(os.getenv("RISK_PER_TRADE","0.01"))

df = exchange.candles(symbol, timeframe, 1000)
d = indicators(df)

position = None
trades = []

for _, row in d.iloc[:-1].iterrows():
    price = float(row.close)

    if position:
        exit_price = None
        reason = ""

        if price <= position["stop"]:
            exit_price, reason = price, "STOP"
        elif price >= position["tp"]:
            exit_price, reason = price, "TP"
        elif exit_signal(row):
            exit_price, reason = price, "TREND"

        if exit_price:
            gross = position["amount"] * exit_price
            cost = position["amount"] * position["entry"]
            pnl = gross - cost - (gross + cost) * fee
            balance += gross - gross * fee
            trades.append({
                "time": row["datetime"], "side": "SELL",
                "price": exit_price, "amount": position["amount"],
                "pnl": pnl, "reason": reason, "balance": balance
            })
            position = None

    elif buy_signal(row):
        risk_cash = balance * risk
        amount = risk_cash / (price * sl)
        cost = amount * price

        if cost <= balance * 0.95:
            balance -= cost + cost * fee
            position = {
                "entry": price, "amount": amount,
                "stop": price * (1-sl), "tp": price * (1+tp)
            }
            trades.append({
                "time": row["datetime"], "side": "BUY",
                "price": price, "amount": amount,
                "pnl": 0, "reason": "SIGNAL", "balance": balance
            })

out = pd.DataFrame(trades)
out.to_csv("backtest_results.csv", index=False)

if out.empty:
    print("Islem olusmadi.")
else:
    sells = out[out.side == "SELL"]
    wins = (sells.pnl > 0).sum()
    losses = (sells.pnl <= 0).sum()
    print("=== BACKTEST ===")
    print("Parite:", symbol)
    print("Timeframe:", timeframe)
    print("Baslangic:", float(os.getenv("STARTING_BALANCE","1000")))
    print("Son bakiye:", round(balance,2))
    print("Tamamlanan islem:", len(sells))
    print("Kazanan:", wins, "Kaybeden:", losses)
    print("Win rate:", round(100*wins/len(sells),2) if len(sells) else 0, "%")
    print("Toplam PNL:", round(sells.pnl.sum(),2))
