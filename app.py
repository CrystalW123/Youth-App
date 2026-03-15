import streamlit as st

st.set_page_config(
    page_title="Youth Fun Place",
    page_icon="🙏🏿",
    layout="wide"
)

st.title("Youth Hub")
st.subheader("Faith, fun and engagement for Youth Ministry")

st.markdown("""
Welcom to the Youth Fun Place

This app has three main sections:
    
    - **Verse & Prayer**: get encouragement based on a life topic
    - **Bible Trivia**: answer questions and get instant feedback
    - **Leader Dashboard**: view engagement and quiz activity

Use the sidebar to navigate between pages.

""")

st.info("Start by opening a page from the sidebar")