import pandas as pd
import plotly.express as px
import streamlit as st

from database import get_balance_history


def render_balance_chart():

    history = get_balance_history()

    if not history:
        return

    df = pd.DataFrame(history)

    fig = px.line(df, x="timestamp", y="total_value", title="Portfolio Value Over Time")

    fig.add_hline(y=10000, line_dash="dash")

    st.plotly_chart(fig, use_container_width=True)
