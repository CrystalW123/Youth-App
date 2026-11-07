import json
import re
import time

import streamlit as st

from utils.auth import require_access
from utils.bible_reader import get_verse_text
from utils.llm import generate_bible_answer
from utils.storage import log_event, save_question_event
from utils.styles import apply_custom_styles

require_access()
apply_custom_styles()

st.sidebar.title("Youth Hub")
st.sidebar.caption("Bible engagement for youth")
st.sidebar.markdown("---")

COOLDOWN_SECONDS = 10
MAX_QUESTION_CHARS = 500
GENERAL_TOPIC = "General"

SUGGESTED_QUESTIONS = [
    "What does the Bible say about fear?",
    "How can I pray when I feel distant from God?",
    "Why does God allow hard things to happen?",
]

st.title("Bible Helper 📖")
st.write("Explore Bible promises by topic, or ask a Bible question.")


# -----------------------------
# Data and helpers
# -----------------------------
@st.cache_data
def load_promise_map():
    with open("data/bible_promises.json", "r", encoding="utf-8") as file:
        return json.load(file)


@st.cache_data(show_spinner=False, ttl=3600)
def load_promises(topic: str):
    """Returns a list of {"reference", "text", "error"} for a topic."""
    promise_map = load_promise_map()
    items = []

    for reference in promise_map.get(topic, []):
        try:
            items.append({"reference": reference, "text": get_verse_text(reference), "error": None})
        except Exception as e:
            items.append({"reference": reference, "text": None, "error": str(e)})

    return items


def render_verse(verse_text: str):
    for block in verse_text.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        match = re.match(r"^(\d+)\.\s+(.*)$", block, re.DOTALL)
        if match:
            st.markdown(
                f"<sup>{match.group(1)}</sup> {match.group(2)}",
                unsafe_allow_html=True,
            )
        else:
            st.write(block)


def use_suggestion(text: str):
    st.session_state.question_input = text


promise_map = load_promise_map()
topics = list(promise_map.keys())

if "question_input" not in st.session_state:
    st.session_state.question_input = ""

if "last_question_time" not in st.session_state:
    st.session_state.last_question_time = 0.0

tab_promises, tab_ask = st.tabs(["📜 Bible Promises", "💬 Ask a Question"])

# -----------------------------
# Tab 1: Promises
# -----------------------------
with tab_promises:
    promise_topic = st.selectbox("Choose a topic", topics, key="promise_topic")

    for item in load_promises(promise_topic):
        with st.container(border=True):
            st.markdown(f"**{item['reference']}**")
            if item["text"]:
                render_verse(item["text"])
            else:
                st.warning(f"Could not load {item['reference']}.")

# -----------------------------
# Tab 2: Ask a question
# -----------------------------
with tab_ask:
    ask_topic = st.selectbox(
        "Related topic (optional)",
        [GENERAL_TOPIC] + topics,
        key="ask_topic",
    )

    st.caption("Not sure what to ask? Try one of these:")
    for i, suggestion in enumerate(SUGGESTED_QUESTIONS):
        st.button(
            suggestion,
            key=f"suggestion_{i}",
            on_click=use_suggestion,
            args=(suggestion,),
            width="stretch",
        )

    question = st.text_area(
        "What would you like to ask?",
        key="question_input",
        max_chars=MAX_QUESTION_CHARS,
        placeholder="Example: What does the Bible say about fear?",
    )

    if st.button("Get Answer", width="stretch", type="primary"):
        seconds_since_last = time.time() - st.session_state.last_question_time

        if not question.strip():
            st.warning("Please enter a question first.")
        elif seconds_since_last < COOLDOWN_SECONDS:
            wait = int(COOLDOWN_SECONDS - seconds_since_last) + 1
            st.warning(f"Please wait {wait} seconds before asking another question.")
        else:
            st.session_state.last_question_time = time.time()

            with st.spinner("Preparing an answer..."):
                try:
                    answer = generate_bible_answer(
                        question=question.strip(),
                        topic=ask_topic,
                    )

                    st.session_state.bible_answer = {
                        "question": question.strip(),
                        "topic": ask_topic,
                        "answer": answer,
                    }

                    # Save only that a question was asked, not the question itself
                    save_question_event(topic=ask_topic, event_type="question_asked")

                    # Also log to usage_logs so asking a question counts toward the daily streak
                    log_event(page="helper", event_type="question_asked", topic=ask_topic)

                except Exception as e:
                    st.session_state.pop("bible_answer", None)
                    print(f"Bible answer failed: {e}")
                    st.error(
                        "The Bible Helper is busy right now. Please try again in a minute, "
                        "or explore the Bible promises in the other tab."
                    )

    saved = st.session_state.get("bible_answer")

    if saved:
        st.markdown("### Answer")
        st.caption(f"Your question: {saved['question']}")
        st.write(saved["answer"])
        st.info(
            "This answer is generated by AI to point you back to Scripture. "
            "Please read the passages yourself and talk with a youth leader about big questions."
        )

        related = load_promises(saved["topic"]) if saved["topic"] in promise_map else []
        related_text = "\n".join(
            f"{item['reference']}\n{item['text']}\n" for item in related if item["text"]
        )

        download_text = (
            "Bible Helper Response\n\n"
            f"Topic: {saved['topic']}\n\n"
            f"Question:\n{saved['question']}\n\n"
            f"Answer:\n{saved['answer']}\n"
        )
        if related_text:
            download_text += f"\nRelated Bible Promises:\n{related_text}"

        st.download_button(
            label="Download this response",
            data=download_text,
            file_name="bible_helper_response.txt",
            mime="text/plain",
            width="stretch",
        )