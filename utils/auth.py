import uuid
import streamlit as st
from supabase import create_client, Client


NAMESPACE = st.secrets["OWN_NAMESPACE"]
CUSTOM_NAMESPACE = uuid.UUID(NAMESPACE)


@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def get_google_user_uuid():
    email = st.user.email.lower().strip()
    return str(uuid.uuid5(CUSTOM_NAMESPACE, email))


def get_guest_uuid(alias: str):
    alias_clean = alias.lower().strip()
    return str(uuid.uuid5(CUSTOM_NAMESPACE, f"guest:{alias_clean}"))


def is_logged_in_user():
    return hasattr(st, "user") and st.user.is_logged_in


def is_guest_user():
    return st.session_state.get("guest_alias") is not None


def can_access_app():
    return is_logged_in_user() or is_guest_user()


def get_current_user_uuid():
    if is_logged_in_user():
        return st.session_state.get("user_uuid") or get_google_user_uuid()

    if is_guest_user():
        return st.session_state.get("guest_uuid")

    return None


def get_current_display_name():
    if is_logged_in_user():
        return st.user.name

    if is_guest_user():
        return st.session_state.guest_alias

    return None


def should_save_user_profile():
    return is_logged_in_user() or is_guest_user()


def should_save_activity_data():
    return is_logged_in_user()


def ensure_guest_user_exists():
    supabase = get_supabase()

    alias = st.session_state.guest_alias.strip()
    user_uuid = get_guest_uuid(alias)

    response = supabase.rpc(
        "ensure_guest_user_exists",
        {
            "p_name": alias,
            "p_user_uuid": user_uuid,
        }
    ).execute()

    returned_uuid = response.data
    st.session_state.guest_uuid = str(returned_uuid)

    return str(returned_uuid)


def ensure_user_exists():
    supabase = get_supabase()

    email = st.user.email.lower().strip()
    name = st.user.name
    user_uuid = get_google_user_uuid()

    response = supabase.rpc(
        "ensure_user_exists",
        {
            "p_email": email,
            "p_name": name,
            "p_user_uuid": user_uuid,
        }
    ).execute()

    returned_uuid = response.data
    st.session_state.user_uuid = str(returned_uuid)

    return str(returned_uuid)


def require_access():
    """
    Put this at the top of every page except app.py.
    It blocks direct page access unless the user signed in or entered an alias.
    """
    if not can_access_app():
        st.warning("Please sign in or enter an alias from the home page to continue.")
        st.page_link("app.py", label="Go to Home", icon="🏠")
        st.stop()