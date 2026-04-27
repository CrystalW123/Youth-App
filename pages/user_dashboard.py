import streamlit as st
import pandas as pd
from collections import Counter
from utils.styles import apply_custom_styles
from utils.storage import get_supabase, get_current_user_email
from utils.auth import require_access
require_access()

apply_custom_styles()

supabase = get_supabase()
user_uuid = st.session_state.get("user_uuid")
user_email = get_current_user_email()

verse_res = (
    supabase.table("verse_requests")
    .select("*")
    .eq("user_uuid", user_uuid)
    .order("created_at", desc=True)
    .execute()
)

trivia_res = (
    supabase.table("trivia_attempts")
    .select("*")
    .eq("user_uuid", user_uuid)
    .order("created_at", desc=True)
    .execute()
)

verse_df = pd.DataFrame(verse_res.data)
trivia_df = pd.DataFrame(trivia_res.data)

st.sidebar.title("Youth Hub")
st.sidebar.caption("Bible engagement for youth")
st.sidebar.markdown("---")

st.title("My Dashboard ✨")
st.caption(f"Signed in as: {user_email}")
st.write("A summary of your activity in this session.")

attempts = len(trivia_df)

correct = (
    trivia_df["is_correct"].sum()
    if not trivia_df.empty and "is_correct" in trivia_df.columns
    else 0
)

accuracy = (correct / attempts * 100) if attempts > 0 else 0

verses_viewed = len(verse_df)

topics_explored = (
    verse_df["topic"].nunique()
    if not verse_df.empty and "topic" in verse_df.columns
    else 0
)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Trivia Answered", attempts)
with col2:
    st.metric("Correct Answers", correct)
with col3:
    st.metric("Accuracy", f"{accuracy:.1f}%")

col1, col2 = st.columns(2)
with col1:
    st.metric("Verses Viewed", verses_viewed)
with col2:
    st.metric("Topics Explored", topics_explored)

st.markdown("## Your Most Explored Topic(s)")
if not verse_df.empty:
    topic_counts = verse_df["topic"].value_counts()

    max_count = topic_counts.max()

    # Get all topics with the max count
    top_topics = topic_counts[topic_counts == max_count].index.tolist()

    if len(top_topics) == 1:
        st.write(f"**{top_topics[0]}**")
        st.caption(f"Explored {max_count} time(s)")
    else:
        st.write("**Top Topics:**")
        for topic in top_topics:
            st.write(f"- {topic}")
        st.caption(f"Each explored {max_count} time(s)")
else:
    st.write("No topics explored yet.")

st.markdown("## Recent Verse References")
if not verse_df.empty:
    recent_verses = verse_df["verse_reference"].head(5)

    for ref in recent_verses:
        st.write(f"- {ref}")
else:
    st.write("No verses viewed yet.")

st.markdown("## Latest Reflection Question")
if not verse_df.empty and "reflection_question" in verse_df.columns:
    latest_question = verse_df["reflection_question"].iloc[0]

    if latest_question:
        st.info(latest_question)
    else:
        st.write("No reflection question yet.")
else:
    st.write("No reflection question yet.")