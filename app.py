import streamlit as st
from utils.styles import apply_custom_styles
from utils.auth import ensure_user_exists, get_guest_uuid, ensure_guest_user_exists

st.set_page_config(page_title="Youth Hub", page_icon="🙏🏿", layout="wide")

apply_custom_styles()

if "guest_alias" not in st.session_state:
    st.session_state.guest_alias = None

if "guest_uuid" not in st.session_state:
    st.session_state.guest_uuid = None

is_logged_in = st.user.is_logged_in
has_alias = st.session_state.guest_alias is not None

if not is_logged_in and not has_alias:
    left, center, right = st.columns([1, 2, 1])

    with center:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("## Welcome to Youth Hub ✨")
        st.write(
            "Sign in to save your progress, view your dashboard, "
            "and keep track of your Bible journey."
        )

        if st.button("Continue with Google", use_container_width=True):
            st.login()

        st.markdown("---")
        st.write("Or continue as a guest. You will not be able to save your progress.")

        alias = st.text_input("Enter your name or alias")

        if st.button("Continue as Guest", use_container_width=True):
            if alias.strip():
                try:
                    st.session_state.guest_alias = alias.strip()
                    st.session_state.guest_uuid = get_guest_uuid(alias.strip())

                    ensure_guest_user_exists()

                    st.rerun()

                except Exception:
                    st.error("That alias is already taken. Please choose another one.")
                    st.session_state.guest_alias = None
                    st.session_state.guest_uuid = None

            else:
                st.warning("Please enter a name or alias to continue.")

    st.stop()

if is_logged_in:
    ensure_user_exists()
    display_name = st.user.name
else:
    ensure_guest_user_exists()
    display_name = st.session_state.guest_alias

st.markdown(f"## Welcome, {display_name} ✨")

st.sidebar.title("Youth Hub")
st.sidebar.caption("Bible engagement for youth")
st.sidebar.markdown("---")

if is_logged_in:
    st.sidebar.caption("Signed in with Google")
else:
    st.sidebar.caption("Guest mode: activity will not be saved")

st.sidebar.markdown("<br><br><br><br><br>", unsafe_allow_html=True)

if is_logged_in:
    if st.sidebar.button("Logout", use_container_width=True):
        st.logout()
else:
    if st.sidebar.button("Exit Guest Mode", use_container_width=True):
        st.session_state.guest_alias = None
        st.session_state.guest_uuid = None
        st.rerun()

# -----------------------------
# Home page
# -----------------------------
st.title("Youth Hub 🙏🏿")
st.subheader("Faith, fun, and engagement for the youth community")

st.markdown(
    "A Bible engagement app built to make Scripture interaction more consistent, fun, and meaningful."
)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("📖 Bible Trivia\n\nTest your Bible knowledge", use_container_width=True):
        st.switch_page("pages/bible_trivia.py")

with col2:
    if st.button("🙏 Verse & Challenge\n\nGet encouragement", use_container_width=True):
        st.switch_page("pages/verse_and_challenge.py")

with col3:
    if st.button("✨ My Dashboard\n\nSee your activity", use_container_width=True):
        st.switch_page("pages/user_dashboard.py")

with col4:
    if st.button("🔒 Leader Dashboard\n\nOnly available to youth leaders", use_container_width=True):
        st.switch_page("pages/leader_dashboard.py")

with col5:
    if st.button("Reviews\n\nPlease give your review", use_container_width=True):
        st.switch_page("pages/reviews.py")

st.markdown("---")
st.success("Use the cards above to explore the app.")