import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Setup Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
spreadsheet = client.open("Magnificent 7")

# --- List of stock symbols / tab names ---
stocks = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA"]

# --- Define headers manually ---
headers = [
    "Date", "Open", "High", "Low", "Close", "Adj Close", "Volume",
    "RSI", "MACD", "MACD_signal", "MACD_hist",
    "BB_upper", "BB_middle", "BB_lower",
    "SMA_50", "SMA_200", "EMA_20"
]

# --- Loop through each sheet and write the full header row at once ---
for symbol in stocks:
    worksheet = spreadsheet.worksheet(symbol)
    worksheet.update(values=[headers], range_name="A1")   # ✅ one single row update
    print(f"✅ Header written to row 1 for {symbol}.")