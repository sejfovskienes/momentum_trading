import pandas as pd
import streamlit as st

from database import (
    get_portfolio
)

from data_fetcher import (
    get_current_price,
    calculate_roc
)

def render_holdings():

    positions = get_portfolio()

    rows = []

    for p in positions:

        current_price = (
            get_current_price(
                p["ticker"]
            )
        )

        current_value = (
            current_price
            * p["shares"]
        )

        pnl = (
            current_price
            - p["avg_buy_price"]
        ) * p["shares"]

        pnl_pct = (
            (
                current_price
                - p["avg_buy_price"]
            )
            / p["avg_buy_price"]
        ) * 100

        rows.append(
            {
                "Ticker": p["ticker"],
                "Shares": round(
                    p["shares"], 4
                ),
                "Avg Buy":
                    p["avg_buy_price"],
                "Current":
                    current_price,
                "Value":
                    current_value,
                "PnL":
                    pnl,
                "PnL %":
                    pnl_pct,
                "ROC":
                    calculate_roc(
                        p["ticker"]
                    )
            }
        )

    st.subheader(
        "Current Holdings"
    )

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True
    )