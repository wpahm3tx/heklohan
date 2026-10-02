import os, time, csv
from dotenv import load_dotenv
from exchange import Exchange
from strategy import indicators, buy_signal, exit_signal
from storage import Store
from notify import telegram

load_dotenv()

EXCHANGE = os.getenv("EXCHANGE", "binance")
SYMBOLS = [x.strip() for x in os.getenv(
    "SYMBOLS", "BTC/USDT,ETH/USDT").split(",") if x.strip()]
TIMEFRAME = os.getenv("TIMEFRAME", "15m")

PAPER = os.getenv("PAPER_TRADING", "true").lower() == "true"
if not PAPER and os.getenv("LIVE_TRADING_CONFIRM", "") != "I_UNDERSTAND":
    raise SystemExit("Canli islem icin LIVE_TRADING_CONFIRM=I_UNDERSTAND gerekli.")

START = float(os.getenv("STARTING_BALANCE", "1000"))
RISK = float(os.getenv("RISK_PER_TRADE", "0.01"))
MAX_POS = int(os.getenv("MAX_OPEN_POSITIONS", "2"))
SL = float(os.getenv("STOP_LOSS_PCT", "0.015"))
TP = float(os.getenv("TAKE_PROFIT_PCT", "0.03"))
FEE = float(os.getenv("FEE_PCT", "0.001"))
POLL = int(os.getenv("POLL_SECONDS", "30"))

ex = Exchange(EXCHANGE, os.getenv("API_KEY",""), os.getenv("API_SECRET",""))
store = Store()
cash = START
positions = {}
last_candle = {}

def notify(msg):
    print(msg)
    telegram(os.getenv("TELEGRAM_BOT_TOKEN",""),
             os.getenv("TELEGRAM_CHAT_ID",""), msg)

def log_csv(row):
    exists = os.path.exists("trades.csv")
    with open("trades.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=row.keys())
        if not exists:
            w.writeheader()
        w.writerow(row)

def open_position(symbol, price):
    global cash
    if len(positions) >= MAX_POS or symbol in positions:
        return

    risk_cash = cash * RISK
    amount = risk_cash / (price * SL)
    cost = amount * price

    if cost > cash * 0.95:
        amount = (cash * 0.95) / price
        cost = amount * price
    if amount <= 0:
        return

    if not PAPER:
        ex.market_order(symbol, "buy", amount)

    cash -= cost + cost * FEE
    positions[symbol] = {
        "entry": price,
        "amount": amount,
        "stop": price * (1 - SL),
        "tp": price * (1 + TP)
    }

    mode = "paper" if PAPER else "live"
    store.trade(symbol, "BUY", price, amount, 0, mode)
    log_csv({
        "time": time.time(), "symbol": symbol, "side": "BUY",
        "price": price, "amount": amount, "pnl": 0, "mode": mode
    })
    notify(f"BUY {symbol} @ {price:.4f} | amount={amount:.6f}")

def close_position(symbol, price, reason):
    global cash
    p = positions.pop(symbol)
    gross = p["amount"] * price
    entry_cost = p["amount"] * p["entry"]
    pnl = gross - entry_cost - (gross + entry_cost) * FEE

    if not PAPER:
        ex.market_order(symbol, "sell", p["amount"])

    cash += gross - gross * FEE
    mode = "paper" if PAPER else "live"
    store.trade(symbol, "SELL", price, p["amount"], pnl, mode)
    log_csv({
        "time": time.time(), "symbol": symbol, "side": "SELL",
        "price": price, "amount": p["amount"], "pnl": pnl, "mode": mode
    })
    notify(f"SELL {symbol} @ {price:.4f} | PNL={pnl:.2f} | {reason}")

while True:
    try:
        for symbol in SYMBOLS:
            df = ex.candles(symbol, TIMEFRAME, 250)
            d = indicators(df)
            if len(d) < 2:
                continue

            # Son kapanmış mum kullanılır; açık mum sinyal üretmez.
            row = d.iloc[-2]
            candle_id = int(df.iloc[-2]["timestamp"])

            if last_candle.get(symbol) == candle_id:
                if symbol in positions:
                    price = ex.last_price(symbol)
                    p = positions[symbol]
                    if price <= p["stop"]:
                        close_position(symbol, price, "STOP")
                    elif price >= p["tp"]:
                        close_position(symbol, price, "TAKE_PROFIT")
                continue

            last_candle[symbol] = candle_id
            price = ex.last_price(symbol)

            if symbol in positions:
                p = positions[symbol]
                if price <= p["stop"]:
                    close_position(symbol, price, "STOP")
                elif price >= p["tp"]:
                    close_position(symbol, price, "TAKE_PROFIT")
                elif exit_signal(row):
                    close_position(symbol, price, "TREND_EXIT")
            elif buy_signal(row):
                open_position(symbol, price)

        print(f"cash={cash:.2f} | positions={list(positions.keys())}")
        time.sleep(POLL)

    except KeyboardInterrupt:
        print("Bot durduruldu.")
        break
    except Exception as e:
        print("HATA:", repr(e))
        time.sleep(POLL)
