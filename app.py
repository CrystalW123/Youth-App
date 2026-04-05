import streamlit as st
from utils.styles import apply_custom_styles
from utils.auth import ensure_user_exists

apply_custom_styles()

st.set_page_config(page_title="Youth Hub", page_icon="✨", layout="wide")


if not st.user.is_logged_in:
    left, center, right = st.columns([1, 2, 1])

    with center:
        st.markdown("<br><br><br>", unsafe_allow_html=True)

        with st.container():
            st.markdown("## Welcome to Youth Hub ✨")
            st.write(
                "Sign in to save your progress, view your dashboard, "
                "and keep track of your Bible journey."
            )

            if st.button(
                "Continue with Google",
                width="stretch"
            ):
                st.login()

        st.markdown("<br>", unsafe_allow_html=True)

    st.stop()

ensure_user_exists()

st.markdown(
    f"""
    <div style="
        padding: 16px;
        border-radius: 14px;
        margin-bottom: 18px;
        font-size: 18px;
        font-weight: 600;
    ">
        Welcome, {st.user.name} ✨
    </div>
    """,
    unsafe_allow_html=True
)

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

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("📖 Bible Trivia\n\nTest your Bible knowledge", width="stretch"):
        st.switch_page("pages/bible_trivia.py")

with col2:
    if st.button("🙏 Verse & Prayer\n\nGet encouragement", width="stretch"):
        st.switch_page("pages/verse_and_prayer.py")

with col3:
    if st.button("✨ My Dashboard\n\nSee your session activity", width="stretch"):
        st.switch_page("pages/user_dashboard.py")

with col4:
    if st.button("🔒 Leader Dashboard\n\nOnly available to youth leaders", width="stretch"):
        st.switch_page("pages/leader_dashboard.py")

with col5:
    if st.button("Reviews\n\nPlease Give your review", width="stretch"):
        st.switch_page("pages/reviews.py")

st.markdown("---")
st.success("Use the sidebar to explore the app.")

st.sidebar.markdown("<bl><bl><bl><bl><bl><bl><bl><bl>", unsafe_allow_html=True)
if st.sidebar.button("Logout", width="stretch"):
    st.logout()