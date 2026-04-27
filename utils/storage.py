import streamlit as st
from datetime import datetime
from supabase import create_client, Client
from utils.auth import should_save_activity_data
import uuid


@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

def get_user_uuid():
    return st.session_state.get("user_uuid")

def get_current_user_email():
    if hasattr(st, "user") and getattr(st.user, "is_logged_in", False):
        return st.user.email
    return "guest"


def get_current_user_name():
    if hasattr(st, "user") and getattr(st.user, "is_logged_in", False):
        return st.user.name
    return "Guest"


def log_event(
    page,
    event_type,
    topic="",
    verse_reference="",
    difficulty="",
    is_correct="",
    used_fallback="",
    user_uuid=None,
):
    if not should_save_activity_data():
        return
    try:
        supabase = get_supabase()

        if user_uuid is None:
            user_uuid = get_user_uuid()

        data = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "page": page,
            "event_type": event_type,
            "topic": topic,
            "verse_reference": verse_reference,
            "difficulty": difficulty,
            "is_correct": str(is_correct),
            "used_fallback": str(used_fallback),
            "user_uuid": user_uuid,
        }

        supabase.table("usage_logs").insert(data).execute()

    except Exception as e:
        print(f"Supabase logging failed: {e}")


def save_verse_request(topic, verse_reference, used_fallback=False, challenge="", reflection_question=""):
    if not should_save_activity_data():
        return
    try:
        supabase = get_supabase()
        supabase.table("verse_requests").insert({
            "user_uuid": get_user_uuid(),
            "topic": topic,
            "verse_reference": verse_reference,
            "used_fallback": used_fallback,
            "challenge": challenge,
            "reflection_question": reflection_question,
        }).execute()
    except Exception as e:
        print(f"Verse request insert failed: {e}")


def save_trivia_attempt(difficulty, question_text, verse_reference, is_correct):
    if not should_save_activity_data():
        return
    try:
        supabase = get_supabase()
        supabase.table("trivia_attempts").insert({
            "user_uuid": get_user_uuid(),
            "difficulty": difficulty,
            "question_text": question_text,
            "verse_reference": verse_reference,
            "is_correct": is_correct,
        }).execute()
    except Exception as e:
        print(f"Trivia attempt insert failed: {e}")


def save_review(rating, review_text):
    try:
        supabase = get_supabase()
        supabase.table("reviews").insert({
            "rating": rating,
            "review_text": review_text,
        }).execute()
    except Exception as e:
        print(f"Review insert failed: {e}")