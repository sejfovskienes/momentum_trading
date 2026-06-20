from data_fetcher import get_current_price
from database import get_meta, get_portfolio


def calculate_portfolio_value():

    positions = get_portfolio()

    total_value = 0.0

    for position in positions:
        current_price = get_current_price(position["ticker"])

        if current_price is None:
            continue

        total_value += position["shares"] * current_price

    return round(total_value, 2)


def calculate_total_value():

    meta = get_meta()

    cash = meta["current_cash"]

    portfolio_value = calculate_portfolio_value()

    return round(cash + portfolio_value, 2)


def unrealized_pnl(position):

    current_price = get_current_price(position["ticker"])

    pnl = (current_price - position["avg_buy_price"]) * position["shares"]

    return pnl
