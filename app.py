import html
import json
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import streamlit as st

from utils.auth import (
    ensure_guest_user_exists,
    ensure_user_exists,
    get_current_display_name,
    get_current_user_uuid,
    get_guest_uuid,
    get_supabase,
)
from utils.bible_reader import get_verse_text
from utils.styles import apply_custom_styles

st.set_page_config(page_title="Youth Hub", page_icon="🙏🏿", layout="wide")
apply_custom_styles()

APP_TZ = ZoneInfo("Africa/Nairobi")

# -----------------------------
# Session state
# -----------------------------
for key in ("guest_alias", "guest_uuid", "profile_for"):
    if key not in st.session_state:
        st.session_state[key] = None

is_logged_in = st.user.is_logged_in
has_alias = st.session_state.guest_alias is not None
is_authed = is_logged_in or has_alias


# -----------------------------
# Helpers
# -----------------------------
def verse_html(verse_text: str) -> str:
    """Turn '16. For God...' blocks into paragraphs with a small verse number."""
    parts = []
    for block in verse_text.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        match = re.match(r"^(\d+)\.\s+(.*)$", block, re.DOTALL)
        if match:
            number, body = match.group(1), match.group(2)
            parts.append(
                f'<p class="verse-text"><sup>{number}</sup> {html.escape(body, quote=False)}</p>'
            )
        else:
            parts.append(f'<p class="verse-text">{html.escape(block, quote=False)}</p>')
    return "".join(parts)


def load_verse_of_the_day_references():
    """
    Hand-picked list from data/verse_of_the_day.json (edit it any time).
    If that file is missing or empty, fall back to every verse in topic_to_verses.json.
    """
    try:
        with open("data/verse_of_the_day.json", "r", encoding="utf-8") as file:
            references = [r.strip() for r in json.load(file) if isinstance(r, str) and r.strip()]
        if references:
            return references
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"verse_of_the_day.json not usable, using topic verses instead: {e}")

    with open("data/topic_to_verses.json", "r", encoding="utf-8") as file:
        topic_map = json.load(file)

    return sorted({ref for refs in topic_map.values() for ref in refs})


@st.cache_data(ttl=3600, show_spinner=False)
def get_verse_of_the_day(day_ordinal: int):
    """
    Same verse for everyone on a given day. If a verse in the list cannot be
    loaded (for example the book name does not match a Bible file), it is
    skipped and the next one is used.
    """
    references = load_verse_of_the_day_references()

    for offset in range(len(references)):
        reference = references[(day_ordinal + offset) % len(references)]
        try:
            return reference, get_verse_text(reference)
        except Exception as e:
            print(f"Verse of the day skipped {reference}: {e}")

    raise RuntimeError("No verse of the day could be loaded")


@st.cache_data(ttl=60, show_spinner=False)
def get_streak(user_uuid: str):
    """Returns (streak_days, active_today) based on the user's logged activity."""
    try:
        rows = (
            get_supabase()
            .table("usage_logs")
            .select("timestamp")
            .eq("user_uuid", user_uuid)
            .order("timestamp", desc=True)
            .limit(1000)
            .execute()
            .data
        )
    except Exception as e:
        print(f"Streak lookup failed: {e}")
        return 0, False

    days = set()
    for row in rows or []:
        try:
            days.add(datetime.fromisoformat(str(row["timestamp"])).date())
        except (KeyError, ValueError):
            continue

    today = datetime.now().date()
    cursor = today if today in days else today - timedelta(days=1)

    streak = 0
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)

    return streak, today in days


def ensure_profile():
    """Create/refresh the user row once per sign-in, not on every rerun."""
    if is_logged_in:
        identity = f"google:{st.user.email}"
    else:
        identity = f"guest:{st.session_state.guest_alias}"

    if st.session_state.profile_for != identity:
        if is_logged_in:
            ensure_user_exists()
        else:
            ensure_guest_user_exists()
        st.session_state.profile_for = identity


def greeting() -> str:
    hour = datetime.now(APP_TZ).hour
    if hour < 12:
        return "Good morning"
    if hour < 17:
        return "Good afternoon"
    return "Good evening"


def nav_card(column, key, icon, title, blurb, page):
    with column:
        with st.container(key=f"card_{key}"):
            st.markdown(f'<div class="card-icon">{icon}</div>', unsafe_allow_html=True)
            st.markdown(f"**{title}**")
            st.markdown(
                f'<div class="card-blurb">{html.escape(blurb)}</div>',
                unsafe_allow_html=True,
            )
            st.page_link(page, label="Open", icon="➡️")


# -----------------------------
# Login screen
# -----------------------------
def show_login():
    _, center, _ = st.columns([1, 2, 1])

    with center:
        st.markdown("<div style='height: 3rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="eyebrow">Youth Hub</div>', unsafe_allow_html=True)
        st.markdown("# Welcome ✨")
        st.write(
            "Sign in to save your progress, see your dashboard, "
            "and keep track of your Bible journey."
        )

        if st.button("Continue with Google", type="primary", width="stretch"):
            st.login()

        st.divider()

        with st.form("guest_form"):
            alias = st.text_input(
                "Or continue as a guest",
                placeholder="Your name or alias",
            )
            st.caption("Guests can explore, but progress is not saved.")
            submitted = st.form_submit_button("Continue as Guest", width="stretch")

        if submitted:
            if alias.strip():
                st.session_state.guest_alias = alias.strip()
                st.session_state.guest_uuid = get_guest_uuid(alias.strip())
                st.rerun()
            else:
                st.warning("Please enter a name or alias to continue.")


# -----------------------------
# Home page
# -----------------------------
def home():
    name = get_current_display_name() or "friend"
    first_name = name.split()[0]

    # Sidebar
    st.sidebar.markdown("### Youth Hub")
    st.sidebar.caption("Bible engagement for youth")
    st.sidebar.divider()

    if is_logged_in:
        st.sidebar.caption("Signed in with Google")
        if st.sidebar.button("Logout", width="stretch"):
            st.session_state.profile_for = None
            st.logout()
    else:
        st.sidebar.caption("Guest mode: activity will not be saved")
        if st.sidebar.button("Exit Guest Mode", width="stretch"):
            st.session_state.guest_alias = None
            st.session_state.guest_uuid = None
            st.session_state.profile_for = None
            st.rerun()

    # Greeting + streak
    if is_logged_in:
        streak, _ = get_streak(get_current_user_uuid())
        chip = f"🔥 {streak}-day streak" if streak >= 1 else "🌱 Start your streak today"
    else:
        chip = "👤 Guest mode"

    st.markdown(
        f'<div class="greet-row"><h2>{greeting()}, {html.escape(first_name)} ✨</h2>'
        f'<span class="chip">{chip}</span></div>',
        unsafe_allow_html=True,
    )

    # Verse of the day
    try:
        reference, verse_text = get_verse_of_the_day(datetime.now(APP_TZ).date().toordinal())
    except Exception as e:
        print(f"Verse of the day failed: {e}")
        reference, verse_text = None, None

    if reference:
        with st.container(key="hero"):
            st.markdown('<div class="eyebrow">Verse of the day</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="verse-ref">{html.escape(reference)}<small>WEB</small></div>'
                f"{verse_html(verse_text)}",
                unsafe_allow_html=True,
            )
            st.page_link(verse_page, label="Get a challenge for today", icon="🙏")

    # Main cards
    st.markdown("### Explore")
    c1, c2, c3, c4 = st.columns(4)

    nav_card(c1, "verse", "🙏", "Verse & Challenge", "Get a verse and a small challenge", verse_page)
    nav_card(c2, "helper", "💬", "Bible Helper", "Ask questions, explore promises", helper_page)
    nav_card(c3, "trivia", "📖", "Bible Trivia", "Test your Bible knowledge", trivia_page)
    nav_card(c4, "progress", "✨", "My Progress", "See your activity", dashboard_page)

    # Quiet footer links
    st.divider()
    f1, f2, _ = st.columns([1, 1, 2])
    with f1:
        st.page_link(reviews_page, label="Share feedback", icon="⭐")
    with f2:
        st.page_link(leader_page, label="Leader dashboard", icon="🔒")


# -----------------------------
# Navigation
# -----------------------------
home_page = st.Page(home, title="Home", default=True)
verse_page = st.Page("pages/verse_and_challenge.py", title="Verse & Challenge")
helper_page = st.Page("pages/questions_and_promises.py", title="Bible Helper")
trivia_page = st.Page("pages/bible_trivia.py", title="Bible Trivia")
dashboard_page = st.Page("pages/user_dashboard.py", title="My Progress")
reviews_page = st.Page("pages/reviews.py", title="Feedback")
leader_page = st.Page("pages/leader_dashboard.py", title="Leader Dashboard")

navigation = st.navigation(
    [
        home_page,
        verse_page,
        helper_page,
        trivia_page,
        dashboard_page,
        reviews_page,
        leader_page,
    ],
    position="sidebar" if is_authed else "hidden",
)

if not is_authed:
    show_login()
    st.stop()

ensure_profile()
navigation.run()