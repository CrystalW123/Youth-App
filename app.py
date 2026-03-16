import streamlit as st
from utils.styles import apply_custom_styles

apply_custom_styles()

st.sidebar.title("Youth Hub")
st.sidebar.caption("Bible engagement for youth")
st.sidebar.markdown("---")

st.set_page_config(
    page_title="Youth Hub",
    page_icon="🙏🏿",
    layout="wide"
)

st.title("Youth Hub 🙏🏿")
st.subheader("Faith, fun, and engagement for the youth community")

st.markdown(
    "A Bible engagement app built to make Scripture interaction more consistent, fun, and meaningful."
)

col1, col2, col3 = st.columns(3)

with col1:
    st.info("**Bible Trivia**\n\nTest your Bible knowledge one question at a time.")

with col2:
    st.info("**Verse & Prayer**\n\nGet encouragement based on real-life topics.")

with col3:
    st.info("**Dashboard**\n\nTrack engagement and see what youth are interacting with.")

st.markdown("---")
st.success("Use the sidebar to explore the app.")