# resilient_ticker_signal_colored.py
import os
import sys
import time
import math
import numpy as np
import pandas as pd

try:
    import yfinance as yf
except Exception:
    yf = None

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

DEFAULT_TICKER = "AAPL"
LOCAL_CSV_DIR = os.path.expanduser("~/Downloads")

YF_INTRADAY_PERIOD = "1mo"
YF_INTRADAY_INTERVAL = "1h"

RETRY_ATTEMPTS = 3
RETRY_SLEEP_BASE = 1.2

def log(msg):
    print(msg, flush=True)

def clean_ticker_for_yf(t):
    return t.replace(".", "-").strip().upper()

def clean_ticker_for_stooq(t):
    t = t.strip().lower()
    if not t.endswith(".us"):
        t = f"{t}.us"
    return t

def have_min_ohlc(df):
    req = {"Open", "High", "Low", "Close"}
    return isinstance(df, pd.DataFrame) and not df.empty and req.issubset(set(df.columns))

def ensure_datetime_index(df):
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date")
    if not isinstance(df.index, pd.DatetimeIndex):
        try:
            first_col = df.columns[0]
            df[first_col] = pd.to_datetime(df[first_col])
            df = df.set_index(first_col)
        except Exception:
            pass
    try:
        df = df.sort_index()
    except Exception:
        pass
    return df

def load_local_csv(ticker):
    patterns = [
        f"{ticker}.csv",
        f"{ticker.upper()}.csv",
        f"{ticker.lower()}.csv",
        f"{ticker.replace('.', '-')}.csv",
    ]
    for name in patterns:
        path = os.path.join(LOCAL_CSV_DIR, name)
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                df = ensure_datetime_index(df)
                if have_min_ohlc(df):
                    return df
            except Exception:
                continue
    return None

def download_yf(ticker):
    if yf is None:
        return None
    yt = clean_ticker_for_yf(ticker)
    last_err = None
    for i in range(RETRY_ATTEMPTS):
        try:
            df = yf.download(
                yt, period=YF_INTRADAY_PERIOD, interval=YF_INTRADAY_INTERVAL,
                auto_adjust=True, progress=False
            )
            if have_min_ohlc(df):
                return ensure_datetime_index(df)
            last_err = "Empty intraday"
        except Exception as e:
            last_err = str(e)
        time.sleep(RETRY_SLEEP_BASE * (i + 1))
    for i in range(RETRY_ATTEMPTS):
        try:
            df = yf.download(
                yt, period="6mo", interval="1d",
                auto_adjust=True, progress=False
            )
            if have_min_ohlc(df):
                return ensure_datetime_index(df)
        except Exception as e:
            last_err = str(e)
        time.sleep(RETRY_SLEEP_BASE * (i + 1))
    return None

def download_stooq(ticker):
    st = clean_ticker_for_stooq(ticker)
    url = f"https://stooq.com/q/d/l/?s={st}&i=d"
    try:
        csv_data = pd.read_csv(url)
        if csv_data is None or csv_data.empty:
            return None
        csv_data.rename(columns={
            "Date": "Date",
            "Open": "Open",
            "High": "High",
            "Low": "Low",
            "Close": "Close",
        }, inplace=True)
        csv_data = ensure_datetime_index(csv_data)
        if have_min_ohlc(csv_data):
            return csv_data
    except Exception:
        return None
    return None

def compute_indicators(df):
    df = df.copy()
    close = df["Close"].astype(float)
    df["SMA5"] = close.rolling(5).mean()
    df["SMA10"] = close.rolling(10).mean()
    delta = close.diff()
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    avg_gain = pd.Series(gain, index=close.index).rolling(7).mean()
    avg_loss = pd.Series(loss, index=close.index).rolling(7).mean()
    rs = avg_gain / avg_loss
    df["RSI7"] = 100 - (100 / (1 + rs))
    ema_fast = close.ewm(span=6, adjust=False).mean()
    ema_slow = close.ewm(span=13, adjust=False).mean()
    macd = ema_fast - ema_slow
    macd_sig = macd.ewm(span=4, adjust=False).mean()
    df["MACD"] = macd
    df["MACDsig"] = macd_sig
    return df

def make_signal(df):
    if df is None or df.empty or len(df) < 15:
        return "NO DATA", {"reason": "insufficient candles"}
    dfe = compute_indicators(df)
    latest = dfe.iloc[-1]
    if any(pd.isna(latest.get(k)) for k in ["SMA5", "SMA10", "RSI7", "MACD", "MACDsig"]):
        return "NO DATA", {"reason": "indicators NaN"}
    cond_buy = (latest["SMA5"] > latest["SMA10"]) and (latest["RSI7"] < 70) and (latest["MACD"] > latest["MACDsig"])
    cond_sell = (latest["SMA5"] < latest["SMA10"]) and (latest["RSI7"] > 30) and (latest["MACD"] < latest["MACDsig"])
    note = {
        "price": round(float(latest["Close"]), 4),
        "SMA5>SMA10": bool(latest["SMA5"] > latest["SMA10"]),
        "RSI7": round(float(latest["RSI7"]), 2),
        "MACD>Signal": bool(latest["MACD"] > latest["MACDsig"]),
    }
    if cond_buy:
        return "BUY", note
    if cond_sell:
        return "SELL", note
    return "HOLD", note

def get_data_anyhow(ticker):
    df = load_local_csv(ticker)
    if have_min_ohlc(df):
        return df, "local_csv"
    df = download_yf(ticker)
    if have_min_ohlc(df):
        return df, "yfinance"
    df = download_stooq(ticker)
    if have_min_ohlc(df):
        return df, "stooq"
    return None, "none"

def main():
    if len(sys.argv) > 1:
        ticker = sys.argv[1].strip()
    else:
        ticker = DEFAULT_TICKER
    log(f"Ticker: {ticker}")
    df, source = get_data_anyhow(ticker)
    if not have_min_ohlc(df):
        log("Signal: NO DATA")
        log("Reason: Could not retrieve OHLCV from local CSV, Yahoo, or Stooq.")
        sys.exit(2)
    sig, details = make_signal(df)
    color = RESET
    if sig == "BUY":
        color = GREEN
    elif sig == "SELL":
        color = RED
    elif sig == "HOLD":
        color = YELLOW
    log(f"Source: {source}")
    log(f"Price: {details.get('price', '-')}")
    log(f"SMA5>SMA10: {details.get('SMA5>SMA10')}, RSI7: {details.get('RSI7')}, MACD>Signal: {details.get('MACD>Signal')}")
    log(f"Signal: {color}{sig}{RESET}")

if __name__ == "__main__":
    main()