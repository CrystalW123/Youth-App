import streamlit as st
import pandas as pd
import os

st.title("Leader Dashboard 📊")
st.write("View engagement and usage across the app.")

log_file = "data/usage_log.csv"

if not os.path.exists(log_file):
    st.info("No usage data yet. Interact with the app first.")
    st.stop()

df = pd.read_csv(log_file)

if df.empty:
    st.info("No usage data yet. Interact with the app first.")
    st.stop()

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
        .map({"true": 1, "false": 0})
        .fillna(0)
    )

# Metrics
total_trivia_attempts = len(trivia_df)
total_verse_requests = len(verse_df)

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

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Trivia Attempts", total_trivia_attempts)

with col2:
    st.metric("Average Trivia %", f"{average_trivia_score:.1f}%")

with col3:
    st.metric("Verse Requests", total_verse_requests)

with col4:
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
    fallback_by_topic = verse_df.groupby("topic")["used_fallback_num"].sum().sort_values(ascending=False)
    st.bar_chart(fallback_by_topic)

st.markdown("## Recent Activity")
st.dataframe(df.sort_values("timestamp", ascending=False), width="stretch")