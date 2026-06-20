from pytz import timezone

APP_NAME = "QUANTIX"

TICKERS = [
    "NVDA",
    "GOOGL",
    "AAPL",
    "AMZN",
    "MSFT",
    "TSLA",
    "META",
    "SPUS",
    "HLAL"
]

STARTING_BALANCE = 10_000.0

TIMEZONE = timezone("US/Eastern")

DB_PATH = "trading_db.json"

ROC_LOOKBACK_DAYS = 5

PRICE_FETCH_PERIOD = "15d"
PRICE_FETCH_INTERVAL = "1d"