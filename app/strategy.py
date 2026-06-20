from datetime import datetime
from uuid import uuid4

import pytz

from config import STARTING_BALANCE, TICKERS
from data_fetcher import calculate_roc, get_current_price
from database import ( 
    add_balance_snapshot,
    add_log,
    get_meta,
    get_position,
    insert_trade,
    save_meta,
    upsert_position,
)
from portfolio import calculate_portfolio_value


def utc_now():
    return datetime.now(pytz.utc).isoformat()


def record_snapshot():

    meta = get_meta()

    portfolio_value = calculate_portfolio_value()

    total_value = portfolio_value + meta["current_cash"]

    add_balance_snapshot(
        timestamp=utc_now(),
        cash_balance=meta["current_cash"],
        portfolio_value=portfolio_value,
        total_value=total_value,
    )


def initialize_portfolio():

    meta = get_meta()

    if meta and meta.get("initialized"):
        return

    allocation = STARTING_BALANCE / len(TICKERS)

    current_cash = 0.0

    for ticker in TICKERS:
        price = get_current_price(ticker)

        if price is None:
            continue

        shares = allocation / price

        upsert_position(
            ticker=ticker, shares=shares, avg_buy_price=price, timestamp=utc_now()
        )

        insert_trade({
            "id": str(uuid4()),
            "ticker": ticker,
            "action": "BUY",
            "price": price,
            "shares": shares,
            "amount_usd": allocation,
            "roc_at_trade": None,
            "timestamp": utc_now(),
            "pnl_usd": None,
            "pnl_pct": None,
            "profitable": None,
        })

    save_meta({
        "initialized": True,
        "init_date": utc_now(),
        "starting_balance": STARTING_BALANCE,
        "current_cash": current_cash,
        "last_strategy_run": None,
    })

    record_snapshot()

    add_log("initialization", "success", "Portfolio initialized")


def buy_position(ticker, cash_amount, roc):

    if cash_amount <= 0:
        return

    price = get_current_price(ticker)

    if price is None:
        return

    shares = cash_amount / price

    upsert_position(
        ticker=ticker, shares=shares, avg_buy_price=price, timestamp=utc_now()
    )

    trade = {
        "id": str(uuid4()),
        "ticker": ticker,
        "action": "BUY",
        "price": price,
        "shares": shares,
        "amount_usd": cash_amount,
        "roc_at_trade": roc,
        "timestamp": utc_now(),
        "pnl_usd": None,
        "pnl_pct": None,
        "profitable": None,
    }

    insert_trade(trade)

    meta = get_meta()

    meta["current_cash"] -= cash_amount

    save_meta(meta)


def sell_position(ticker, roc):

    position = get_position(ticker)

    if not position:
        return

    current_price = get_current_price(ticker)

    if current_price is None:
        return

    shares = position["shares"]

    amount = shares * current_price

    pnl_usd = (current_price - position["avg_buy_price"]) * shares

    pnl_pct = (
        (current_price - position["avg_buy_price"]) / position["avg_buy_price"]
    ) * 100

    insert_trade({
        "id": str(uuid4()),
        "ticker": ticker,
        "action": "SELL",
        "price": current_price,
        "shares": shares,
        "amount_usd": amount,
        "roc_at_trade": roc,
        "timestamp": utc_now(),
        "pnl_usd": pnl_usd,
        "pnl_pct": pnl_pct,
        "profitable": pnl_usd > 0,
    })

    upsert_position(ticker=ticker, shares=0, avg_buy_price=0, timestamp=utc_now())

    meta = get_meta()

    meta["current_cash"] += amount

    save_meta(meta)


def run_daily_strategy():

    try:
        meta = get_meta()

        today = datetime.utcnow().date().isoformat()

        if meta.get("last_strategy_run") and meta["last_strategy_run"][:10] == today:
            return

        positive_tickers = []

        for ticker in TICKERS:
            roc = calculate_roc(ticker)

            if roc is None:
                continue

            position = get_position(ticker)

            if roc > 0:
                positive_tickers.append(ticker)

                if not position:
                    continue

            else:
                if position:
                    sell_position(ticker, roc)

        cash = get_meta()["current_cash"]

        if positive_tickers and cash > 0:
            allocation = cash / len(positive_tickers)

            for ticker in positive_tickers:
                if get_position(ticker):
                    continue

                buy_position(ticker, allocation, calculate_roc(ticker))

        meta = get_meta()

        meta["last_strategy_run"] = utc_now()

        save_meta(meta)

        record_snapshot()

        add_log("daily_strategy", "success", "Executed successfully")

    except Exception as e:
        add_log("daily_strategy", "error", str(e))


def run_weekly_rebalance():

    try:
        positive = []

        for ticker in TICKERS:
            roc = calculate_roc(ticker)

            if roc is None:
                continue

            if roc > 0:
                positive.append(ticker)

            else:
                if get_position(ticker):
                    sell_position(ticker, roc)

        if not positive:
            record_snapshot()

            return

        cash = get_meta()["current_cash"]

        allocation = cash / len(positive)

        for ticker in positive:
            if get_position(ticker):
                continue

            buy_position(ticker, allocation, calculate_roc(ticker))

        record_snapshot()

        add_log("weekly_rebalance", "success", "Completed")

    except Exception as e:
        add_log("weekly_rebalance", "error", str(e))
