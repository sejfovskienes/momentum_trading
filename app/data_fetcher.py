import pandas as pd
import streamlit as st
import yfinance as yf

from config import PRICE_FETCH_INTERVAL, PRICE_FETCH_PERIOD
from utils import app_level_print


# --- Historical prices ---
@st.cache_data(ttl=300)
def get_price_history(ticker):
    app_level_print(
        f"Fetching price history for ticker '{ticker}' from Yahoo Finance..."
    )
    try:
        df = yf.download(
            ticker,
            period=PRICE_FETCH_PERIOD,
            interval=PRICE_FETCH_INTERVAL,
            auto_adjust=False,
            progress=False,
        )

        return df

    except Exception:
        return pd.DataFrame()


# --- Current price ---


@st.cache_data(ttl=300)
def get_current_price(ticker):
    app_level_print(
        f"Fetching current price for ticker '{ticker}' from Yahoo Finance..."
    )
    df = get_price_history(ticker)

    if df.empty:
        return None

    if "Adj Close" in df.columns:
        return float(df["Adj Close"].iloc[-1])

    return float(df["Close"].iloc[-1])


# --- ROC Calculation ---


def calculate_roc(ticker):
    app_level_print(f"Calculating Rate of Change (ROC) for ticker '{ticker}'...")
    df = get_price_history(ticker)

    if len(df) < 6:
        return None

    if "Adj Close" in df.columns:
        prices = df["Adj Close"]
    else:
        prices = df["Close"]

    current_price = prices.iloc[-1]
    previous_price = prices.iloc[-6]

    roc = ((current_price - previous_price) / previous_price) * 100

    return round(float(roc), 2)


# --- 30 Day data ---


@st.cache_data(ttl=300)
def get_30_day_data(ticker):
    app_level_print(
        f"Fetching 30-day price data for ticker '{ticker}' from Yahoo Finance..."
    )
    try:
        df = yf.download(
            ticker, period="30d", interval="1d", auto_adjust=False, progress=False
        )

        return df

    except Exception:
        return pd.DataFrame()
