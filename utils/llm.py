import os
import re
import json
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))
app_url = st.secrets.get("APP_URL", "http://localhost:8501")

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": app_url,
        "X-OpenRouter-Title": "Youth Bible App",
    },
)

# Tried in order. Free models are often rate limited, so consider adding
# one cheap paid model at the end as a last resort.
MODELS = [
    "stepfun/step-3.5-flash:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nvidia/llama-nemotron-rerank-vl-1b-v2:free",
]

REQUEST_TIMEOUT_SECONDS = 30


def _extract_json(text: str) -> dict:
    """Pull a JSON object out of a model reply, even if it has code fences or extra text."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model reply")

    return json.loads(match.group(0))


def _complete(system: str, prompt: str, temperature: float, parse=None):
    """
    Try each model in order. Returns parse(content) if a parser is given,
    otherwise the stripped text. A model is skipped if it errors, returns
    nothing, or its reply fails parsing.
    """
    last_error = None

    for model_name in MODELS:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )

            content = (response.choices[0].message.content or "").strip()
            if not content:
                raise ValueError("Empty reply")

            return parse(content) if parse else content

        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(f"All LLM models failed. Last error: {last_error}")


def _parse_challenge(content: str) -> dict:
    data = _extract_json(content)
    challenge = str(data.get("challenge", "")).strip()
    question = str(data.get("reflection_question", "")).strip()

    if not challenge or not question:
        raise ValueError("Missing challenge or reflection_question")

    return {"challenge": challenge, "reflection_question": question}


def generate_challenge_and_question(topic: str, reference: str, verse_text: str):
    prompt = f"""
You are helping generate a short, respectful and truthful Christian encouragement for a youth app.

Topic: {topic}
Bible Reference: {reference}
Verse Text: {verse_text}

Return valid JSON with exactly these keys:
- challenge
- reflection_question

Rules:
- challenge: a small challenge related to the verse, such as reading the chapter, or reaching out to show love today or this week. It must be easy, free, and completely safe.
- reflection_question: 1 thoughtful question
- stay grounded in the verse provided
- do not invent extra Bible references
- do not include markdown
- output only the JSON object, nothing else
"""

    return _complete(
        system="You produce concise Christian encouragement in valid JSON.",
        prompt=prompt,
        temperature=0.7,
        parse=_parse_challenge,
    )


def generate_bible_answer(question: str, topic: str) -> str:
    """Returns a plain-text answer (not JSON)."""
    topic_line = f"Topic: {topic}\n" if topic and topic != "General" else ""

    prompt = f"""
You are a respectful Christian Bible helper for young adults.

{topic_line}User Question: {question}

Answer the question in a simple, encouraging way.
Rules:
- Keep it short and practical (under 150 words)
- Write plain text, no JSON and no headings
- Point the user back to reading the Bible
- Do not claim certainty where Scripture is nuanced
- Do not invent Bible verses or references
- If the person mentions self-harm, abuse, or being in danger, respond with care and encourage them to talk to a trusted adult, their youth leader, or local emergency services right away
- End with one suggestion for a passage they can read next, starting with "Read next:"
"""

    return _complete(
        system="You are a concise, kind Christian Bible helper. Reply in plain text.",
        prompt=prompt,
        temperature=0.5,
    )