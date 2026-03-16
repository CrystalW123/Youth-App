import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }

    h1, h2, h3 {
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        padding: 16px;
        border-radius: 18px;
    }

    div.stButton > button {
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        width: 100%;
    }

    div[data-testid="stAlert"] {
        border-radius: 14px;
    }

    div[data-testid="stRadio"] > div {
        padding: 10px;
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)