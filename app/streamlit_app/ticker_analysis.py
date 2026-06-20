import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from config import TICKERS
from database import (
    get_trades_by_ticker
)
from data_fetcher import (
    get_30_day_data,
    calculate_roc
)


#--- Ticker selector---

def render_ticker_analysis():

    st.subheader(
        "Ticker Deep Dive"
    )

    ticker = st.selectbox(
        "Select Ticker",
        TICKERS
    )

    df = get_30_day_data(
        ticker
    )

    if df.empty:
        return


#--- Statistics ---

    prices = df["Close"]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Min",
        round(prices.min(), 2)
    )

    c2.metric(
        "Max",
        round(prices.max(), 2)
    )

    c3.metric(
        "Mean",
        round(prices.mean(), 2)
    )

    c4.metric(
        "ROC",
        f"{calculate_roc(ticker)}%"
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=prices,
            mode="lines",
            name="Price"
        )
    )

    trades = (
        get_trades_by_ticker(
            ticker
        )
    )

    for trade in trades:

        symbol = (
            "triangle-up"
            if trade["action"] == "BUY"
            else "triangle-down"
        )

        fig.add_trace(
            go.Scatter(
                x=[trade["timestamp"]],
                y=[trade["price"]],
                mode="markers",
                marker_symbol=symbol,
                marker_size=12,
                name=trade["action"]
            )
        )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader(
        "Trade History"
    )

    trade_df = pd.DataFrame(
        trades
    )

    st.dataframe(
        trade_df.sort_values(
            "timestamp",
            ascending=False
        ),
        use_container_width=True
    )