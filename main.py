import yfinance as yf
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Google Sheets Setup ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
spreadsheet = client.open("Magnificent 7")

# --- Technical Indicator Functions ---
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_macd(series, short=12, long=26, signal=9):
    ema_short = series.ewm(span=short, adjust=False).mean()
    ema_long = series.ewm(span=long, adjust=False).mean()
    macd = ema_short - ema_long
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    hist = macd - signal_line
    return macd, signal_line, hist

def calculate_bollinger_bands(series, window=20, num_std=2):
    sma = series.rolling(window=window).mean()
    std = series.rolling(window=window).std()
    upper = sma + num_std * std
    lower = sma - num_std * std
    return upper, sma, lower

# --- Fixed Headers ---
headers = [
    "Date", "Open", "High", "Low", "Close", "Adj Close", "Volume",
    "RSI", "MACD", "MACD_signal", "MACD_hist",
    "BB_upper", "BB_middle", "BB_lower",
    "SMA_50", "SMA_200", "EMA_20"
]

# --- Stock Symbols ---
stocks = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA"]

# --- Main Loop ---
for symbol in stocks:
    print(f"\n📥 Processing {symbol}...")

    df = yf.download(symbol, start="2024-01-01", interval="1d")

    df["RSI"] = calculate_rsi(df["Close"])
    df["MACD"], df["MACD_signal"], df["MACD_hist"] = calculate_macd(df["Close"])
    df["BB_upper"], df["BB_middle"], df["BB_lower"] = calculate_bollinger_bands(df["Close"])
    df["SMA_50"] = df["Close"].rolling(window=50).mean()
    df["SMA_200"] = df["Close"].rolling(window=200).mean()
    df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()

    df = df.reset_index()
    df["Date"] = df["Date"].astype(str)
    df = df.round(2).fillna("")

    for col in headers:
        if col not in df.columns:
            df[col] = ""
    df = df[headers]

    try:
        worksheet = spreadsheet.worksheet(symbol)
    except gspread.exceptions.WorksheetNotFound:
        print(f"{symbol}: ❌ Worksheet not found, skipping.")
        continue

    # ✅ Read existing data and extract existing dates from column A (skip header)
    existing_data = worksheet.get_all_values()
    existing_dates = set(
        row[0] for row in existing_data[1:] if row and len(row) > 0 and row[0].strip()
    )

    # ✅ Filter new rows
    new_rows = df[~df["Date"].isin(existing_dates)]

    if not new_rows.empty:
        worksheet.append_rows(new_rows.values.tolist())
        print(f"{symbol}: ✅ {len(new_rows)} new rows appended.")
    else:
        print(f"{symbol}: ⏸️ No new data to append.")