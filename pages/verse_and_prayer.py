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

st.title("Verse & Prayer 🙏")
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
    "generated_prayer": None,
    "generated_reflection_question": None,
    "llm_error": None,
    "used_fallback": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Reset state when topic changes
if st.session_state.selected_topic != selected_topic:
    st.session_state.selected_topic = selected_topic
    st.session_state.selected_verse_reference = None
    st.session_state.selected_verse_text = None
    st.session_state.generated_explanation = None
    st.session_state.generated_prayer = None
    st.session_state.generated_reflection_question = None
    st.session_state.llm_error = None
    st.session_state.used_fallback = False

if st.button("Get Verse"):
    verse_options = topic_map[selected_topic]
    chosen_reference = random.choice(verse_options)

    # Reset current output
    st.session_state.selected_verse_reference = None
    st.session_state.selected_verse_text = None
    st.session_state.generated_explanation = None
    st.session_state.generated_prayer = None
    st.session_state.generated_reflection_question = None
    st.session_state.llm_error = None
    st.session_state.used_fallback = False

    # Step 1: Load verse from local files
    try:
        verse_text = get_verse_text(chosen_reference)
        st.session_state.selected_verse_reference = chosen_reference
        st.session_state.selected_verse_text = verse_text
    except Exception as e:
        st.session_state.selected_verse_reference = chosen_reference
        st.error(f"Verse loading failed: {e}")
        st.stop()

    # Step 2: Try LLM first
    try:
        llm_output = generate_explanation_and_prayer(
            topic=selected_topic,
            reference=chosen_reference,
            verse_text=verse_text
        )
        st.session_state.generated_explanation = llm_output.get("explanation")
        st.session_state.generated_prayer = llm_output.get("prayer")
        st.session_state.generated_reflection_question = llm_output.get("reflection_question")

    except Exception as e:
        st.session_state.llm_error = str(e)

        fallback_output = generate_fallback_content(
            topic=selected_topic,
            reference=chosen_reference
        )
        st.session_state.generated_explanation = fallback_output["explanation"]
        st.session_state.generated_prayer = fallback_output["prayer"]
        st.session_state.generated_reflection_question = fallback_output["reflection_question"]
        st.session_state.used_fallback = True

    log_event(
    page="verse",
    event_type="verse_request",
    topic=selected_topic,
    verse_reference=chosen_reference,
    used_fallback=st.session_state.used_fallback,
    )

if st.session_state.selected_verse_reference:
    st.subheader("Selected Verse for You")
    st.write(f"**{st.session_state.selected_verse_reference}**")
    st.text(st.session_state.selected_verse_text)

    if st.session_state.used_fallback:
        st.info("AI generation is busy right now, so a built-in encouragement was used instead.")

    if st.session_state.generated_explanation:
        st.markdown("### Short Explanation")
        st.write(st.session_state.generated_explanation)

    if st.session_state.generated_prayer:
        st.markdown("### Prayer")
        st.write(st.session_state.generated_prayer)

    if st.session_state.generated_reflection_question:
        st.markdown("### Reflection Question")
        st.write(st.session_state.generated_reflection_question)