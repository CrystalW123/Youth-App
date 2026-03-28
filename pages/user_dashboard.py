import streamlit as st
import pandas as pd
from collections import Counter
from utils.styles import apply_custom_styles

apply_custom_styles()

st.sidebar.title("Youth Hub")
st.sidebar.caption("Bible engagement for youth")
st.sidebar.markdown("---")

st.title("My Dashboard ✨")
st.write("A summary of your activity in this session.")

# Defaults
if "session_trivia_attempts" not in st.session_state:
    st.session_state.session_trivia_attempts = 0

if "session_trivia_correct" not in st.session_state:
    st.session_state.session_trivia_correct = 0

if "session_verse_requests" not in st.session_state:
    st.session_state.session_verse_requests = []

if "session_topics_used" not in st.session_state:
    st.session_state.session_topics_used = []

if "session_last_reflection_question" not in st.session_state:
    st.session_state.session_last_reflection_question = None

attempts = st.session_state.session_trivia_attempts
correct = st.session_state.session_trivia_correct
accuracy = (correct / attempts * 100) if attempts > 0 else 0
verses_viewed = len(st.session_state.session_verse_requests)

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
    st.metric("Topics Explored", len(set(st.session_state.session_topics_used)))

st.markdown("## Most Explored Topic")
if st.session_state.session_topics_used:
    topic_counts = Counter(st.session_state.session_topics_used)
    top_topic, top_count = topic_counts.most_common(1)[0]
    st.write(f"**{top_topic}** ({top_count} time(s))")
else:
    st.write("No topics explored yet.")

st.markdown("## Recent Verse References")
if st.session_state.session_verse_requests:
    for ref in st.session_state.session_verse_requests[-5:][::-1]:
        st.write(f"- {ref}")
else:
    st.write("No verses viewed yet.")

st.markdown("## Latest Reflection Question")
if st.session_state.session_last_reflection_question:
    st.info(st.session_state.session_last_reflection_question)
else:
    st.write("No reflection question yet.")