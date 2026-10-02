# Crypto Trading Bot

Varsayılan olarak PAPER TRADING yapan kripto trading botu.

## Özellikler
- CCXT ile borsa bağlantısı
- Binance spot varsayılanı
- BTC/USDT, ETH/USDT ve seçilebilir pariteler
- EMA 9/21 + RSI + MACD stratejisi
- Stop-loss / take-profit
- Risk bazlı pozisyon büyüklüğü
- Maksimum açık pozisyon
- Paper trading
- Backtest
- SQLite işlem günlüğü
- CSV işlem raporu
- Telegram bildirimleri (opsiyonel)
- Canlı işlem modu varsayılan olarak kapalı

## Kurulum

Python 3.11+ önerilir.

    python -m venv .venv

Windows:

    .venv\Scripts\activate

macOS/Linux:

    source .venv/bin/activate

    pip install -r requirements.txt

`.env.example` dosyasını `.env` olarak kopyala.

Paper trading için API anahtarı şart değildir.

Önemli ayarlar:
- EXCHANGE=binance
- SYMBOLS=BTC/USDT,ETH/USDT
- TIMEFRAME=15m
- PAPER_TRADING=true
- STARTING_BALANCE=1000
- RISK_PER_TRADE=0.01
- STOP_LOSS_PCT=0.015
- TAKE_PROFIT_PCT=0.03

## Paper trading

    python bot.py

## Backtest

    python backtest.py

Sonuç `backtest_results.csv` dosyasına yazılır.

## Canlı işlem

Canlı işlem risklidir. Önce paper trading ve backtest yap.

`.env` içinde:

    PAPER_TRADING=false
    LIVE_TRADING_CONFIRM=I_UNDERSTAND
    API_KEY=...
    API_SECRET=...

API anahtarında para çekme iznini açma.

Bu bot kâr garantisi vermez. Geçmiş performans gelecekteki sonucu garanti etmez.
