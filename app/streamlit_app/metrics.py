import streamlit as st

from database import get_all_trades, get_meta
from portfolio import calculate_total_value


def render_kpis():

    meta = get_meta()

    cash = meta["current_cash"]

    total_value = calculate_total_value()

    return_pct = ((total_value - 10000) / 10000) * 100

    trade_count = len(get_all_trades())

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("💰 Portfolio Value", f"${total_value:,.2f}")

    c2.metric("📦 Cash", f"${cash:,.2f}")

    c3.metric("📈 Return", f"{return_pct:.2f}%")

    c4.metric("🔄 Trades", trade_count)
