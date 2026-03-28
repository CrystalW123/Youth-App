import streamlit as st
import json
import random
from utils.bible_reader import get_verse_text
from utils.llm import generate_explanation_and_prayer
from utils.fallback import generate_fallback_content
from utils.storage import log_event
from utils.styles import apply_custom_styles

apply_custom_styles()

st.sidebar.title("Youth Hub")
st.sidebar.caption("Bible engagement for youth")
st.sidebar.markdown("---")

st.title("Verse for the Day 🙏")
st.write("Choose a topic and get a Bible verse and encouragement.")

with open("data/topic_to_verses.json", "r", encoding="utf-8") as file:
    topic_map = json.load(file)

topics = list(topic_map.keys())
selected_topic = st.selectbox("Choose topic", topics)

# Session state setup
defaults = {
    "selected_topic": selected_topic,
    "selected_verse_reference": None,
    "selected_verse_text": None,
    "generated_explanation": None,
    "generated_reflection_question": None,
    "llm_error": None,
    "used_fallback": False,
    "is_generating": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


@st.cache_data(show_spinner=False, ttl=3600)
def get_cached_generation(topic: str, reference: str, verse_text: str):
    """
    Cache LLM/fallback output for 1 hour so repeated requests
    for the same verse do not hit the LLM again.
    """
    try:
        llm_output = generate_explanation_and_prayer(
            topic=topic,
            reference=reference,
            verse_text=verse_text
        )
        return {
            "explanation": llm_output.get("explanation"),
            "reflection_question": llm_output.get("reflection_question"),
            "llm_error": None,
            "used_fallback": False,
        }
    except Exception as e:
        fallback_output = generate_fallback_content(
            topic=topic,
            reference=reference
        )
        return {
            "explanation": fallback_output["explanation"],
            "reflection_question": fallback_output["reflection_question"],
            "llm_error": str(e),
            "used_fallback": True,
        }


def reset_output():
    st.session_state.selected_verse_reference = None
    st.session_state.selected_verse_text = None
    st.session_state.generated_explanation = None
    st.session_state.generated_reflection_question = None
    st.session_state.llm_error = None
    st.session_state.used_fallback = False


# Reset state when topic changes
if st.session_state.selected_topic != selected_topic:
    st.session_state.selected_topic = selected_topic
    reset_output()

# Buttons side by side
col1, col2 = st.columns([1, 1])

with col1:
    get_verse_clicked = st.button(
        "Get Verse",
        disabled=st.session_state.is_generating,
        use_container_width=True
    )

with col2:
    try_another_clicked = st.button(
        "Try Another",
        disabled=st.session_state.is_generating,
        use_container_width=True
    )

if get_verse_clicked or try_another_clicked:
    verse_options = topic_map[selected_topic]

    if try_another_clicked and st.session_state.selected_verse_reference:
        available_options = [
            ref for ref in verse_options
            if ref != st.session_state.selected_verse_reference
        ]

        if available_options:
            chosen_reference = random.choice(available_options)
        else:
            chosen_reference = st.session_state.selected_verse_reference
    else:
        chosen_reference = random.choice(verse_options)

    reset_output()
    st.session_state.is_generating = True

    # Step 1: Load verse from local files
    try:
        verse_text = get_verse_text(chosen_reference)
        st.session_state.selected_verse_reference = chosen_reference
        st.session_state.selected_verse_text = verse_text
    except Exception as e:
        st.session_state.selected_verse_reference = chosen_reference
        st.session_state.is_generating = False
        st.error(f"Verse loading failed: {e}")
        st.stop()

    # Step 2: Generate/cached response
    with st.spinner("Preparing your encouragement please wait..."):
        result = get_cached_generation(
            topic=selected_topic,
            reference=chosen_reference,
            verse_text=verse_text
        )

    st.session_state.generated_explanation = result["explanation"]
    st.session_state.generated_reflection_question = result["reflection_question"]
    st.session_state.llm_error = result["llm_error"]
    st.session_state.used_fallback = result["used_fallback"]
    st.session_state.is_generating = False

    if "session_verse_requests" not in st.session_state:
        st.session_state.session_verse_requests = []

    if "session_topics_used" not in st.session_state:
        st.session_state.session_topics_used = []

    if "session_last_reflection_question" not in st.session_state:
        st.session_state.session_last_reflection_question = None

    st.session_state.session_verse_requests.append(chosen_reference)
    st.session_state.session_topics_used.append(selected_topic)
    st.session_state.session_last_reflection_question = st.session_state.generated_reflection_question

    log_event(
        page="verse",
        event_type="verse_request",
        topic=selected_topic,
        verse_reference=chosen_reference,
        used_fallback=st.session_state.used_fallback,
    )

if st.session_state.selected_verse_reference:
    with st.container():
        st.subheader("Selected Verse for You (WEB)")
        st.write(f"**{st.session_state.selected_verse_reference}**")
        st.text(st.session_state.selected_verse_text)

    if st.session_state.used_fallback:
        st.info("AI generation is busy right now, so a built-in encouragement was used instead.")

    if st.session_state.generated_explanation:
        st.markdown("### Short Explanation")
        st.write(st.session_state.generated_explanation)

    if st.session_state.generated_reflection_question:
        st.markdown("### Reflection Question")
        st.write(st.session_state.generated_reflection_question)