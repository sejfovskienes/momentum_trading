from datetime import datetime

import pytz
import streamlit as st

from database import get_meta


def render_sidebar():

    st.sidebar.title("Trading Controls")

    eastern = pytz.timezone("US/Eastern")

    now = datetime.now(eastern)

    st.sidebar.write(f"Current Time: {now}")

    meta = get_meta()

    if meta:
        st.sidebar.write(f"Last Run: {meta.get('last_strategy_run')}")

    refresh = st.sidebar.button("🔄 Refresh Prices")

    strategy = st.sidebar.button("⚡ Run Strategy Now")

    rebalance = st.sidebar.button("♻️ Run Rebalance Now")

    return (refresh, strategy, rebalance)
