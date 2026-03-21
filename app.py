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

st.markdown("""
<style>
div.stButton > button {
    height: 120px;
    border-radius: 16px;
    font-size: 16px;
    font-weight: 600;
    text-align: left;
    padding: 16px;
    white-space: pre-line;
}
div.stButton > button:hover {
    background-color: rgba(255,0,0,0.08);
    transform: translateY(-2px);
    box-shadow: 0 0 20px rgba(108, 99, 255, 0.5);
}
div.stButton > button {
    transition: all 0.2s ease;
}
</style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Bible Trivia\n\nTest your Bible knowledge one question at a time", use_container_width=True):
        st.switch_page("pages/bible_trivia.py")

with col2:
    if st.button("🙏 Verse & Prayer\n\nGet encouragement based on real life topics", use_container_width=True):
        st.switch_page("pages/verse_prayer.py")

with col3:
    if st.button("📈 Dashboard\n\nView engagement insights and see what youth are interacting with", use_container_width=True):
        st.switch_page("pages/leader_dashboard.py")

st.markdown("---")
st.success("Use the sidebar to explore the app.")