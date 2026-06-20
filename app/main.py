import streamlit as st

from config import APP_NAME
from scheduler import start_scheduler
from strategy import initialize_portfolio
from streamlit_app.charts import render_balance_chart
from streamlit_app.holdings import render_holdings
from streamlit_app.metrics import render_kpis
from streamlit_app.sidebar import render_sidebar
from streamlit_app.styles import load_styles
from streamlit_app.ticker_analysis import render_ticker_analysis
from utils import app_level_print

app_level_print(f"Starting {APP_NAME} Dashboard...")
st.set_page_config(
    page_title="Momentum Trading Dashboard", page_icon="📈", layout="wide"
)

initialize_portfolio()

if "scheduler_started" not in st.session_state:
    start_scheduler()

    st.session_state["scheduler_started"] = True

load_styles()

refresh, run_strategy, run_rebalance = render_sidebar()

if refresh:
    st.rerun()

if run_strategy:
    from app.strategy import run_daily_strategy

    run_daily_strategy()

    st.rerun()

if run_rebalance:
    from strategy import run_weekly_rebalance

    run_weekly_rebalance()

    st.rerun()

st.title(f"📈 {APP_NAME} Trading Dashboard")

render_kpis()

render_balance_chart()

render_holdings()

render_ticker_analysis()
