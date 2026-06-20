import streamlit as st


def load_styles():

    st.markdown(
        """
        <style>

        .positive {
            color: green;
            font-weight: bold;
        }

        .negative {
            color: red;
            font-weight: bold;
        }

        </style>
        """,
        unsafe_allow_html=True
    )