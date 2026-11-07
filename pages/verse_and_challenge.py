import json
import random
import re

import streamlit as st

from utils.auth import require_access
from utils.bible_reader import get_verse_text
from utils.fallback import generate_fallback_content
from utils.llm import generate_challenge_and_question
from utils.storage import log_event, save_verse_request
from utils.styles import apply_custom_styles

require_access()
apply_custom_styles()

st.sidebar.title("Youth Hub")
st.sidebar.caption("Bible engagement for youth")
st.sidebar.markdown("---")

st.title("Verse for the Day 🙏")
st.write("Choose a topic and get a Bible verse and encouragement.")


# -----------------------------
# Data and helpers
# -----------------------------
@st.cache_data
def load_topic_map():
    with open("data/topic_to_verses.json", "r", encoding="utf-8") as file:
        return json.load(file)


@st.cache_data(show_spinner=False, ttl=3600)
def get_cached_llm(topic: str, reference: str, verse_text: str):
    """
    Only successful LLM results are cached (for 1 hour).
    If this raises, Streamlit does not cache the failure,
    so the next request tries the LLM again.
    """
    output = generate_challenge_and_question(
        topic=topic,
        reference=reference,
        verse_text=verse_text,
    )
    return {
        "challenge": output["challenge"],
        "reflection_question": output["reflection_question"],
    }


def get_generation(topic: str, reference: str, verse_text: str):
    try:
        result = get_cached_llm(topic, reference, verse_text)
        return {**result, "llm_error": None, "used_fallback": False}
    except Exception as e:
        fallback = generate_fallback_content(topic=topic, reference=reference)
        return {
            "challenge": fallback["challenge"],
            "reflection_question": fallback["reflection_question"],
            "llm_error": str(e),
            "used_fallback": True,
        }


def render_verse(verse_text: str):
    """Show each verse as wrapped text with a small verse number."""
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


topic_map = load_topic_map()
topics = list(topic_map.keys())
selected_topic = st.selectbox("Choose topic", topics)

# -----------------------------
# Session state
# -----------------------------
defaults = {
    "selected_topic": selected_topic,
    "selected_verse_reference": None,
    "selected_verse_text": None,
    "generated_challenge": None,
    "generated_reflection_question": None,
    "llm_error": None,
    "used_fallback": False,
    "challenges_done": set(),
    "session_verse_requests": [],
    "session_topics_used": [],
    "session_last_reflection_question": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def reset_output():
    st.session_state.selected_verse_reference = None
    st.session_state.selected_verse_text = None
    st.session_state.generated_challenge = None
    st.session_state.generated_reflection_question = None
    st.session_state.llm_error = None
    st.session_state.used_fallback = False


# Reset the shown verse when the topic changes
if st.session_state.selected_topic != selected_topic:
    st.session_state.selected_topic = selected_topic
    reset_output()

# -----------------------------
# Buttons
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    get_verse_clicked = st.button("Get Verse", width="stretch")

with col2:
    try_another_clicked = st.button("Try Another", width="stretch")

if get_verse_clicked or try_another_clicked:
    verse_options = topic_map[selected_topic]
    current_reference = st.session_state.selected_verse_reference

    if try_another_clicked and current_reference:
        choices = [ref for ref in verse_options if ref != current_reference] or verse_options
    else:
        choices = verse_options

    chosen_reference = random.choice(choices)

    # Step 1: load the verse from the local files
    try:
        verse_text = get_verse_text(chosen_reference)
    except Exception as e:
        reset_output()
        st.error(f"Could not load {chosen_reference}: {e}")
        st.stop()

    # Step 2: generate encouragement (LLM, or built-in fallback)
    with st.spinner("Preparing your encouragement, please wait..."):
        result = get_generation(
            topic=selected_topic,
            reference=chosen_reference,
            verse_text=verse_text,
        )

    st.session_state.selected_verse_reference = chosen_reference
    st.session_state.selected_verse_text = verse_text
    st.session_state.generated_challenge = result["challenge"]
    st.session_state.generated_reflection_question = result["reflection_question"]
    st.session_state.llm_error = result["llm_error"]
    st.session_state.used_fallback = result["used_fallback"]

    # Session tracking
    st.session_state.session_verse_requests.append(chosen_reference)
    st.session_state.session_topics_used.append(selected_topic)
    st.session_state.session_last_reflection_question = result["reflection_question"]

    # Saving (these helpers skip guests automatically)
    save_verse_request(
        topic=selected_topic,
        verse_reference=chosen_reference,
        used_fallback=st.session_state.used_fallback,
        challenge=st.session_state.generated_challenge or "",
        reflection_question=st.session_state.generated_reflection_question or "",
    )

    log_event(
        page="verse",
        event_type="verse_request",
        topic=selected_topic,
        verse_reference=chosen_reference,
        used_fallback=st.session_state.used_fallback,
    )

# -----------------------------
# Output
# -----------------------------
reference = st.session_state.selected_verse_reference

if reference:
    with st.container(border=True):
        st.subheader("Your Verse (WEB)")
        st.write(f"**{reference}**")
        render_verse(st.session_state.selected_verse_text)

    if st.session_state.used_fallback:
        st.info("AI generation is busy right now, so a built-in encouragement was used instead.")

    if st.session_state.generated_challenge:
        st.markdown("### Short Challenge")
        st.write(st.session_state.generated_challenge)
        if not st.session_state.used_fallback:
            st.caption(
                "This challenge is generated by AI to encourage living out your faith "
                "and reading the Bible."
            )

        already_done = reference in st.session_state.challenges_done

        if already_done:
            st.success("Nice work! You completed this challenge ✅")
        elif st.button("I did it ✅", key=f"done_{reference}"):
            st.session_state.challenges_done.add(reference)
            log_event(
                page="verse",
                event_type="challenge_done",
                topic=selected_topic,
                verse_reference=reference,
                used_fallback=st.session_state.used_fallback,
            )
            st.toast("Well done! 🙌")
            st.rerun()

    if st.session_state.generated_reflection_question:
        st.markdown("### Reflection Question")
        st.write(st.session_state.generated_reflection_question)

    with st.expander("Share this with a friend"):
        share_text = (
            f"{reference} (WEB)\n"
            f"{st.session_state.selected_verse_text}\n\n"
            f"Challenge: {st.session_state.generated_challenge}\n"
            f"Reflect: {st.session_state.generated_reflection_question}"
        )
        st.caption("Use the copy icon at the top right of the box, then paste into WhatsApp.")
        st.code(share_text, language=None, wrap_lines=True)