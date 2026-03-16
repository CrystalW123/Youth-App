import os
import json
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost:8501",
        "X-OpenRouter-Title": "Youth Bible App",
    },
)

MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "stepfun/step-3.5-flash:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "z-ai/glm-4.5-air:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "arcee-ai/trinity-mini:free"
]

def generate_explanation_and_prayer(topic: str, reference: str, verse_text: str):
    prompt = f"""
You are helping generate a short, respectful and truthful Christian encouragement for a youth app.

Topic: {topic}
Bible Reference: {reference}
Verse Text: {verse_text}

Return valid JSON with exactly these keys:
- explanation
- prayer
- reflection_question

Rules:
- explanation: 2 short sentences, simple language for young adults
- prayer: 2 short sentences
- reflection_question: 1 thoughtful question
- stay grounded in the verse provided
- do not invent extra Bible references
- do not include markdown
"""

    last_error = None

    for model_name in MODELS:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You produce concise Christian encouragement in valid JSON."
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )

            content = response.choices[0].message.content.strip()

            if content.startswith("```"):
                content = content.replace("```json", "").replace("```", "").strip()

            return json.loads(content)

        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(f"All LLM models failed. Last error: {last_error}")