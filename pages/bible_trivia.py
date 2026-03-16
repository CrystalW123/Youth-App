import streamlit as st
import pandas as pd
import random
from utils.storage import log_event
from utils.styles import apply_custom_styles

apply_custom_styles()

st.sidebar.title("Youth Hub")
st.sidebar.caption("Bible engagement for youth")
st.sidebar.markdown("---")

st.title("Bible Trivia ❓")
st.write("Test your Bible knowledge one question at a time.")

# Load CSV
df = pd.read_csv("data/trivia_questions.csv")
df = df.reset_index().rename(columns={"index": "question_id"})

# Difficulty choice
difficulty = st.selectbox("Choose level", ["Easy", "Medium", "Hard"])

# Session state setup
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False

if "selected_difficulty" not in st.session_state:
    st.session_state.selected_difficulty = difficulty

if "current_question" not in st.session_state:
    st.session_state.current_question = None

if "shuffled_options" not in st.session_state:
    st.session_state.shuffled_options = None

if "answered" not in st.session_state:
    st.session_state.answered = False

if "question_number" not in st.session_state:
    st.session_state.question_number = 0

if "used_questions" not in st.session_state:
    st.session_state.used_questions = {
        "Easy": [],
        "Medium": [],
        "Hard": []
    }

if "score" not in st.session_state:
    st.session_state.score = {
        "Easy": 0,
        "Medium": 0,
        "Hard": 0
    }

if "questions_seen" not in st.session_state:
    st.session_state.questions_seen = {
        "Easy": 0,
        "Medium": 0,
        "Hard": 0
    }

if "answer_recorded" not in st.session_state:
    st.session_state.answer_recorded = False

if "quiz_completed" not in st.session_state:
    st.session_state.quiz_completed = {
        "Easy": False,
        "Medium": False,
        "Hard": False
    }


def reset_level(level):
    st.session_state.used_questions[level] = []
    st.session_state.score[level] = 0
    st.session_state.questions_seen[level] = 0
    st.session_state.current_question = None
    st.session_state.shuffled_options = None
    st.session_state.answered = False
    st.session_state.answer_recorded = False
    st.session_state.quiz_completed[level] = False
    st.session_state.question_number += 1


def load_new_question(filtered_df, level):
    used_ids = st.session_state.used_questions[level]
    available_df = filtered_df[~filtered_df["question_id"].isin(used_ids)]

    if available_df.empty:
        st.session_state.quiz_completed[level] = True
        st.session_state.current_question = None
        st.session_state.shuffled_options = None
        return

    question_row = available_df.sample(1).iloc[0]
    st.session_state.current_question = question_row
    st.session_state.used_questions[level].append(question_row["question_id"])

    options = [
        question_row["Option_1"],
        question_row["Option_2"],
        question_row["Option_3"],
        question_row["Option_4"]
    ]
    random.shuffle(options)

    st.session_state.shuffled_options = options
    st.session_state.answered = False
    st.session_state.answer_recorded = False


# Reset state if difficulty changes
if st.session_state.selected_difficulty != difficulty:
    st.session_state.selected_difficulty = difficulty
    st.session_state.quiz_started = False
    st.session_state.current_question = None
    st.session_state.shuffled_options = None
    st.session_state.answered = False
    st.session_state.answer_recorded = False
    st.session_state.question_number += 1

# Filter by selected level
filtered_df = df[df["Level"].str.lower() == difficulty.lower()]

if filtered_df.empty:
    st.warning(f"No questions found for {difficulty} level yet.")
    st.stop()

total_questions = len(filtered_df)

col1, col2 = st.columns(2)

with col1:
    if not st.session_state.quiz_started:
        if st.button("Start Quiz"):
            reset_level(difficulty)
            st.session_state.quiz_started = True
            load_new_question(filtered_df, difficulty)
            st.rerun()

with col2:
    if st.session_state.quiz_started:
        if st.button("Restart Quiz"):
            reset_level(difficulty)
            load_new_question(filtered_df, difficulty)
            st.rerun()

# Stop if quiz has not started
if not st.session_state.quiz_started:
    st.info(f"Click Start Quiz to begin the {difficulty} level.")
    st.stop()

# Quiz completed state
if st.session_state.quiz_completed[difficulty]:
    final_score = st.session_state.score[difficulty]
    final_total = total_questions
    percentage = (final_score / final_total) * 100 if final_total > 0 else 0

    st.success(f"You scored {final_score} out of {final_total} in {difficulty}.")
    st.metric("Percentage Score", f"{percentage:.1f}%")

    if st.button("Play Again"):
        reset_level(difficulty)
        load_new_question(filtered_df, difficulty)
        st.rerun()

    st.stop()

# Load first question if needed
if st.session_state.current_question is None:
    load_new_question(filtered_df, difficulty)

question_data = st.session_state.current_question
options = st.session_state.shuffled_options

question = question_data["Question"]
correct_answer = question_data["Answer"]
verse = question_data["Verse"]

score = st.session_state.score[difficulty]
answered_so_far = st.session_state.questions_seen[difficulty]
current_progress = min(answered_so_far, total_questions)
percentage_live = (score / answered_so_far * 100) if answered_so_far > 0 else 0

st.caption(f"Level: {difficulty}")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Score", score)
with col2:
    st.metric("Progress", f"{current_progress} of {total_questions}")
with col3:
    st.metric("Percentage", f"{percentage_live:.1f}%")

st.subheader(question)

radio_key = f"selected_option_{difficulty}_{st.session_state.question_number}"

selected = st.radio(
    "Choose your answer:",
    options,
    key=radio_key,
    disabled=st.session_state.answered
)

if not st.session_state.answered:
    if st.button("Submit Answer"):
        st.session_state.answered = True

        if not st.session_state.answer_recorded:
            st.session_state.questions_seen[difficulty] += 1
            is_correct = selected == correct_answer

            if is_correct:
                st.session_state.score[difficulty] += 1

            log_event(
                page="trivia",
                event_type="trivia_answer",
                difficulty=difficulty,
                is_correct=is_correct,
                verse_reference=verse,
                topic=question
            )

            st.session_state.answer_recorded = True

        st.rerun()

else:
    if selected == correct_answer:
        st.success("Correct ✅")
        st.write(f"Comes from the verse **{verse}**")
    else:
        st.error("Wrong ❌")
        st.write(f"The correct answer is **{correct_answer}**")
        st.write(f"Comes from the verse **{verse}**")

    if st.button("Next Question"):
        st.session_state.question_number += 1
        load_new_question(filtered_df, difficulty)
        st.rerun()