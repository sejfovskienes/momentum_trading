from threading import Lock

from tinydb import Query, TinyDB
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage

from config import DB_PATH
from utils import app_level_print

db_lock = Lock()

db = TinyDB(DB_PATH, storage=CachingMiddleware(JSONStorage))

portfolio_table = db.table("portfolio")
trades_table = db.table("trades")
balance_table = db.table("balance_history")
meta_table = db.table("meta")
logs_table = db.table("execution_logs")

Q = Query()


# --- Meta operations ---


def get_meta():
    app_level_print("Fetching meta data from database...")
    records = meta_table.all()
    return records[0] if records else None


def save_meta(meta_data):
    app_level_print("Saving meta data to database...")
    with db_lock:
        meta_table.truncate()
        meta_table.insert(meta_data)
        db.storage.flush()


# --- Portfolio operations ---


def get_portfolio():
    app_level_print("Fetching portfolio data from database...")
    return portfolio_table.all()


def get_position(ticker):
    app_level_print(f"Fetching position for ticker '{ticker}' from database...")
    result = portfolio_table.search(Q.ticker == ticker)

    if result:
        return result[0]

    return None


def upsert_position(ticker, shares, avg_buy_price, timestamp):
    app_level_print(f"Upserting position for ticker '{ticker}' in database...")
    with db_lock:
        existing = get_position(ticker)

        if shares <= 0:
            portfolio_table.remove(Q.ticker == ticker)

        elif existing:
            portfolio_table.update(
                {
                    "shares": shares,
                    "avg_buy_price": avg_buy_price,
                    "last_updated": timestamp,
                },
                Q.ticker == ticker,
            )

        else:
            portfolio_table.insert({
                "ticker": ticker,
                "shares": shares,
                "avg_buy_price": avg_buy_price,
                "last_updated": timestamp,
            })

        db.storage.flush()


# --- Trade operations ---


def insert_trade(trade):
    app_level_print(f"Inserting trade for ticker '{trade['ticker']}' into database...")
    with db_lock:
        trades_table.insert(trade)
        db.storage.flush()


def get_all_trades():
    return trades_table.all()


def get_trades_by_ticker(ticker):
    return trades_table.search(Q.ticker == ticker)


# --- Balance history operations ---


def add_balance_snapshot(timestamp, cash_balance, portfolio_value, total_value):
    app_level_print(
        f"Adding balance snapshot at timestamp '{timestamp}' into database..."
    )
    with db_lock:
        balance_table.insert({
            "timestamp": timestamp,
            "cash_balance": cash_balance,
            "portfolio_value": portfolio_value,
            "total_value": total_value,
        })

        db.storage.flush()


def get_balance_history():
    return balance_table.all()


# --- Execution logs operations ---


def add_log(job_name, status, message):
    app_level_print(
        f"Adding execution log for job '{job_name}' with status '{status}' into database..."
    )
    with db_lock:
        logs_table.insert({"job": job_name, "status": status, "message": message})

        db.storage.flush()
