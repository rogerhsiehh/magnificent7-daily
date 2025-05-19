import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Connect to Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
spreadsheet = client.open("Magnificent 7")
worksheet = spreadsheet.worksheet("Data")

# --- Define headers with Ticker ---
headers = [
    "Date", "Ticker", "Open", "High", "Low", "Close", "Adj Close", "Volume",
    "RSI", "MACD", "MACD_signal", "MACD_hist",
    "BB_upper", "BB_middle", "BB_lower",
    "SMA_50", "SMA_200", "EMA_20"
]

# --- Write headers to row 1 ---
worksheet.update(range_name="A1", values=[headers])
print("✅ Header written to row 1 in 'Data' tab.")