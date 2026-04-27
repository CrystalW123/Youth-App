import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
from utils.styles import apply_custom_styles
from utils.storage import get_supabase
from utils.auth import require_access
require_access()

apply_custom_styles()

last_week = datetime.now(timezone.utc) - timedelta(days=7)
last_week_iso = last_week.isoformat()

st.sidebar.title("Youth Hub")
st.sidebar.caption("Bible engagement for youth")
st.sidebar.markdown("---")

st.title("Leader Dashboard 📊")
st.caption("Showing data from the last 7 days")

dashboard_password = st.secrets.get("LEADER_DASHBOARD_PASSWORD")

if "leader_access_granted" not in st.session_state:
    st.session_state.leader_access_granted = False

if not st.session_state.leader_access_granted:
    st.warning("This page is only available to the youth leaders.")

    entered_password = st.text_input(
        "Enter leader password",
        type="password"
    )

    if st.button("Unlock Dashboard"):
        if entered_password == dashboard_password:
            st.session_state.leader_access_granted = True
            st.rerun()
        else:
            st.error("Incorrect password.")

    st.stop()

st.write("View engagement and usage across the app.")

supabase = get_supabase()

# Pull usage logs for last week
logs_res = (
    supabase.table("usage_logs")
    .select("*")
    .gte("timestamp", last_week_iso)
    .order("timestamp", desc=True)
    .execute()
)

logs_data = logs_res.data if logs_res.data else []

if not logs_data:
    st.info("No usage data yet. Interact with the app first.")
    st.stop()

df = pd.DataFrame(logs_data)

# Pull reviews too for a week
reviews_res = (
    supabase.table("reviews")
    .select("*")
    .gte("created_at", last_week_iso)
    .order("created_at", desc=True)
    .execute()
)

reviews_data = reviews_res.data if reviews_res.data else []
reviews_df = pd.DataFrame(reviews_data) if reviews_data else pd.DataFrame()

# Ensure expected columns exist
expected_columns = [
    "timestamp",
    "page",
    "event_type",
    "topic",
    "verse_reference",
    "difficulty",
    "is_correct",
    "used_fallback",
    "user_uuid",
]

for col in expected_columns:
    if col not in df.columns:
        df[col] = ""

# Clean timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

# Split event types
trivia_df = df[df["event_type"] == "trivia_answer"].copy()
verse_df = df[df["event_type"] == "verse_request"].copy()

# Safe boolean conversion
def to_bool_num(series):
    return (
        series.fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        .map({"true": 1, "false": 0, "1": 1, "0": 0})
        .fillna(0)
    )

# Metrics
total_trivia_attempts = len(trivia_df)
total_verse_requests = len(verse_df)
total_users = df["user_uuid"].replace("", pd.NA).dropna().nunique()

if not trivia_df.empty:
    trivia_df["is_correct_num"] = to_bool_num(trivia_df["is_correct"])
    average_trivia_score = trivia_df["is_correct_num"].mean() * 100
else:
    average_trivia_score = 0

if not verse_df.empty:
    verse_df["used_fallback_num"] = to_bool_num(verse_df["used_fallback"])
    fallback_count = int(verse_df["used_fallback_num"].sum())
else:
    fallback_count = 0

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Users", total_users)

with col2:
    st.metric("Trivia Attempts", total_trivia_attempts)

with col3:
    st.metric("Average Trivia %", f"{average_trivia_score:.1f}%")

with col4:
    st.metric("Verse Requests", total_verse_requests)

with col5:
    st.metric("Fallback Uses", fallback_count)

st.markdown("## Trivia Insights")

if trivia_df.empty:
    st.write("No trivia data yet.")
else:
    st.markdown("### Plays by Difficulty")
    difficulty_counts = trivia_df["difficulty"].fillna("Unknown").value_counts()
    st.bar_chart(difficulty_counts)

    st.markdown("### Accuracy by Difficulty")
    accuracy_by_level = trivia_df.groupby("difficulty")["is_correct_num"].mean() * 100
    st.bar_chart(accuracy_by_level)

    st.markdown("### Most Active Trivia Users")
    active_trivia_users = (
        trivia_df["user_uuid"]
        .fillna("Unknown")
        .replace("", "Unknown")
        .value_counts()
        .head(10)
    )
    st.bar_chart(active_trivia_users)

st.markdown("## Verse & Prayer Insights")

if verse_df.empty:
    st.write("No verse request data yet.")
else:
    st.markdown("### Most Requested Topics")
    topic_counts = verse_df["topic"].fillna("Unknown").value_counts()
    st.bar_chart(topic_counts)

    st.markdown("### Most Shown Verses")
    verse_counts = verse_df["verse_reference"].fillna("Unknown").value_counts().head(10)
    st.bar_chart(verse_counts)

    st.markdown("### Fallback Usage by Topic")
    fallback_by_topic = (
        verse_df.groupby("topic")["used_fallback_num"]
        .sum()
        .sort_values(ascending=False)
    )
    st.bar_chart(fallback_by_topic)

    st.markdown("### Most Active Verse Users")
    active_verse_users = (
        verse_df["user_uuid"]
        .fillna("Unknown")
        .replace("", "Unknown")
        .value_counts()
        .head(10)
    )
    st.bar_chart(active_verse_users)

st.markdown("## Reviews")

if reviews_df.empty:
    st.write("No reviews yet.")
else:
    if "rating" in reviews_df.columns:
        average_rating = reviews_df["rating"].mean()
        st.metric("Average Rating", f"{average_rating:.1f}/5")

    st.markdown("### Latest Reviews")
    display_cols = [col for col in ["created_at", "user_email", "rating", "review_text"] if col in reviews_df.columns]
    st.dataframe(reviews_df[display_cols], width="stretch")

st.markdown("## Recent Activity")
st.dataframe(
    df.sort_values("timestamp", ascending=False),
    width="stretch"
)