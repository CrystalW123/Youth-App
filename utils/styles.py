import streamlit as st


def apply_custom_styles():
    st.markdown("""
    <style>
    :root {
        --accent: #F5B841;
        --accent-soft: rgba(245, 184, 65, 0.14);
        --accent-line: rgba(245, 184, 65, 0.40);
    }

    .block-container {
        padding-top: 4rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }

    h1, h2, h3 {
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        padding: 16px;
        border-radius: 18px;
    }

    div.stButton > button {
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        width: 100%;
    }

    div[data-testid="stAlert"] {
        border-radius: 14px;
    }

    div[data-testid="stRadio"] > div {
        padding: 10px;
        border-radius: 12px;
    }

    /* ---------- Home page ---------- */

    .greet-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        flex-wrap: wrap;
        padding-top: 0.75rem;
        margin-bottom: 1rem;
    }

    .greet-row h2 {
        margin: 0;
        padding: 0;
    }

    .chip {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 999px;
        background: var(--accent-soft);
        border: 1px solid var(--accent-line);
        color: var(--accent);
        font-weight: 600;
        font-size: 0.9rem;
        white-space: nowrap;
    }

    .eyebrow {
        color: var(--accent);
        letter-spacing: 0.12em;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 6px;
    }

    .verse-ref {
        font-size: 1.3rem;
        font-weight: 700;
        margin: 0 0 10px 0;
    }

    .verse-ref small {
        font-size: 0.75rem;
        font-weight: 600;
        opacity: 0.6;
        margin-left: 6px;
    }

    .verse-text {
        font-size: 1.05rem;
        line-height: 1.7;
        margin: 0 0 8px 0;
    }

    .card-icon {
        font-size: 2rem;
        line-height: 1;
        margin-bottom: 8px;
    }

    /* Reserve two lines so every card ends up the same height */
    .card-blurb {
        font-size: 0.875rem;
        line-height: 1.4;
        min-height: 2.8em;
        opacity: 0.7;
        margin-bottom: 0.5rem;
    }

    .verse-quote {
        font-size: 1.1rem;
        line-height: 1.7;
        padding: 14px 18px;
        margin: 8px 0 16px 0;
        border-left: 3px solid var(--accent);
        background: rgba(255,255,255,0.04);
        border-radius: 0 12px 12px 0;
    }

    .st-key-hero {
        background: linear-gradient(135deg, rgba(245,184,65,0.10), rgba(120,90,255,0.12));
        border: 1px solid var(--accent-line);
        border-radius: 20px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.5rem;
    }

    [class*="st-key-card_"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 18px;
        padding: 1.1rem 1.2rem;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }

    [class*="st-key-card_"]:hover {
        transform: translateY(-2px);
        border-color: var(--accent-line);
    }

    @media (max-width: 640px) {
        .card-blurb {
            min-height: 0;
        }
        .st-key-hero {
            padding: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)