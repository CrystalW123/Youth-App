import uuid
import streamlit as st
from supabase import create_client, Client

NAMESPACE = st.secrets["OWN_NAMESPACE"]

CUSTOM_NAMESPACE = uuid.UUID(NAMESPACE)


def get_current_user_uuid():
    email = st.user.email.lower().strip()
    return str(uuid.uuid5(CUSTOM_NAMESPACE, email))

@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def ensure_user_exists():
    supabase = get_supabase()

    email = st.user.email
    name = st.user.name
    user_uuid = get_current_user_uuid()

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