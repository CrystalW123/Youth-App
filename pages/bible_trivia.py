import streamlit as st
import pandas as pd
import random

st.title("Bible Trivia")

st.write("This page will show on question at a time")

# Load CSV
df = pd.read_csv("data/trivia_questions.csv")

# Difficulty Choice
difficulty = st.selectbox("Choose level", ["Easy", "Medium", "Hard"])

if "selected_difficulty" not in st.session_state:
    st.session_state.selected_difficulty = difficulty

if "current_question" not in st.session_state:
    st.session_state.current_question = None

if "answered" not in st.session_state:
    st.session_state.answered = False

# If difficulty changes, reset question state
if st.session_state.selected_difficulty != difficulty:
    st.session_state.selected_difficulty = difficulty
    st.session_state.current_question = None
    st.session_state.answered = False

filtered_df = df[df["Level"].str.lower() == difficulty.lower()]

if filtered_df.empty:
    st.warning(f"No question found for {difficulty} level yet")
    st.stop()

# Load a random question if none exists
if st.session_state.current_question is None:
    st.session_state.current_question = filtered_df.sample(1).iloc[0]
    st.session_state.answered = False

question_data = st.session_state.current_question

question = question_data["Question"]
options = [
    question_data["Option_1"],
    question_data["Option_2"],
    question_data["Option_3"],
    question_data["Option_4"]
]

# options = random.shuffle(options)

correct_answer = question_data["Answer"]
verse = question_data["Verse"]

st.subheader(question)
st.caption(f"Level: {difficulty.capitalize()}")


selected = st.radio(
    "Choose your answer:",
    options,
    disabled=st.session_state.answered
)

if not st.session_state.answered:
    if st.button("Submit Answer"):
        st.session_state.answered = True

        if selected == correct_answer:
            st.success("Correct ✅")
            st.write(f"Comes from the verse **{verse}**")
        else:
            st.error("Wrong ❌")
            st.write(f"The correct answer is **{correct_answer}**")
            st.write(f"Comes from the verse **{verse}**")
else:
    # Show result again after rerun
    if selected == correct_answer:
        st.success("Correct ✅")
        st.write(f"Comes from the verse **{verse}**")
    else:
        st.error("Wrong ❌")
        st.write(f"The correct answer is **{correct_answer}**")
        st.write(f"Comes from the verse **{verse}**")

    if st.button("Next Question"):
        st.session_state.current_question = filtered_df.sample(1).iloc[0]
        st.session_state.answered = False
        st.rerun()