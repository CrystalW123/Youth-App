"""
Trivia question builder.

Builds multiple-choice questions straight from the verses already in your data
files, so trivia works offline and never depends on the LLM being available.
This module has no Streamlit code, so it is easy to test on its own.

Levels:
    easy   - "Which book of the Bible is this verse from?"
    medium - "Fill in the missing word"
    hard   - "Which verse is this?" (pick the reference)
"""
import random
import re

DIFFICULTIES = ("easy", "medium", "hard")
QUESTIONS_PER_ROUND = 5

BOOKS = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "Ruth",
    "1 Samuel", "2 Samuel", "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra",
    "Nehemiah", "Esther", "Job", "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon",
    "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah",
    "Malachi", "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians",
    "2 Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians",
    "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus", "Philemon",
    "Hebrews", "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude",
    "Revelation",
]

# Common longer words that would make a poor "missing word" or poor distractor.
STOPWORDS = {
    "about", "after", "again", "against", "also", "because", "before", "being", "could",
    "every", "other", "shall", "should", "their", "there", "these", "those", "through",
    "under", "until", "where", "which", "while", "whose", "would", "unto", "upon", "without",
    "whom", "yours", "have", "will", "your", "them", "than", "then", "what", "when",
    "from", "with", "this", "that", "they", "were", "been", "into", "even",
}

_WORD_PATTERN = re.compile(r"^[^A-Za-z]*([A-Za-z]{5,})[^A-Za-z]*$")


# -----------------------------
# Small helpers
# -----------------------------
def clean_verse_text(raw: str) -> str:
    """'16. For God...\\n\\n17. ...' -> 'For God... ...' (verse numbers removed)."""
    parts = []
    for block in raw.split("\n\n"):
        block = re.sub(r"^\d+\.\s+", "", block.strip())
        if block:
            parts.append(block)
    return " ".join(parts)


def book_of(reference: str) -> str:
    match = re.match(r"^(.*?)\s+\d+:\d+", reference.strip())
    return match.group(1).strip() if match else reference.strip()


def _book_key(name: str) -> str:
    """Treat 'Psalm' and 'Psalms' as the same book when picking wrong answers."""
    return re.sub(r"s$", "", name.lower().replace(" ", ""))


def _candidate_word(token: str):
    match = _WORD_PATTERN.match(token)
    if not match:
        return None
    word = match.group(1)
    return None if word.lower() in STOPWORDS else word


def _word_pool(pool: dict) -> set:
    words = set()
    for text in pool.values():
        for token in text.split():
            word = _candidate_word(token)
            if word:
                words.add(word.lower())
    return words


def _shuffled(correct: str, wrong: list, rng: random.Random) -> list:
    options = [correct] + list(wrong)
    rng.shuffle(options)
    return options


# -----------------------------
# Question types
# -----------------------------
def make_book_question(reference: str, text: str, rng: random.Random):
    answer = book_of(reference)
    answer_key = _book_key(answer)
    others = [b for b in BOOKS if _book_key(b) != answer_key]

    return {
        "difficulty": "easy",
        "prompt": "Which book of the Bible is this verse from?",
        "verse": text,
        "options": _shuffled(answer, rng.sample(others, 3), rng),
        "answer": answer,
        "reference": reference,
        "explanation": f"This verse is from {reference}.",
    }


def make_blank_question(reference: str, text: str, word_pool: set, rng: random.Random):
    tokens = text.split()
    candidates = [i for i, tok in enumerate(tokens) if _candidate_word(tok)]
    if not candidates:
        return None

    index = rng.choice(candidates)
    token = tokens[index]
    answer = _candidate_word(token).lower()

    close = sorted(w for w in word_pool if w != answer and abs(len(w) - len(answer)) <= 2)
    anywhere = sorted(w for w in word_pool if w != answer)
    source = close if len(close) >= 3 else anywhere
    if len(source) < 3:
        return None

    fmt = str.capitalize if token.lstrip("“‘\"'(")[:1].isupper() else str.lower
    blanked = tokens.copy()
    blanked[index] = re.sub(r"[A-Za-z]+", "_____", token, count=1)

    return {
        "difficulty": "medium",
        "prompt": "Fill in the missing word.",
        "verse": " ".join(blanked),
        "options": _shuffled(fmt(answer), [fmt(w) for w in rng.sample(source, 3)], rng),
        "answer": fmt(answer),
        "reference": reference,
        "explanation": f"The missing word was \"{fmt(answer)}\" ({reference}).",
    }


def make_reference_question(reference: str, text: str, all_refs: list, rng: random.Random):
    others = [r for r in all_refs if r != reference]
    if len(others) < 3:
        return None

    # Make it tougher: prefer wrong answers from the same book when possible
    same_book = [r for r in others if book_of(r) == book_of(reference)]
    wrong = rng.sample(same_book, min(2, len(same_book)))
    rest = [r for r in others if r not in wrong]
    wrong += rng.sample(rest, 3 - len(wrong))

    return {
        "difficulty": "hard",
        "prompt": "Which verse is this?",
        "verse": text,
        "options": _shuffled(reference, wrong, rng),
        "answer": reference,
        "reference": reference,
        "explanation": f"This verse is {reference}.",
    }


# -----------------------------
# Rounds
# -----------------------------
def build_round(pool: dict, difficulty: str, count: int = QUESTIONS_PER_ROUND, rng=None) -> list:
    """
    pool: {reference: clean verse text}
    Returns up to `count` questions, each from a different verse.
    """
    if difficulty not in DIFFICULTIES:
        raise ValueError(f"Unknown difficulty: {difficulty}")

    rng = rng or random.Random()
    references = sorted(pool)
    rng.shuffle(references)
    word_pool = _word_pool(pool) if difficulty == "medium" else set()

    questions = []
    for reference in references:
        text = pool[reference]

        if difficulty == "easy":
            question = make_book_question(reference, text, rng)
        elif difficulty == "medium":
            question = make_blank_question(reference, text, word_pool, rng)
        else:
            question = make_reference_question(reference, text, references, rng)

        if question:
            questions.append(question)
        if len(questions) >= count:
            break

    return questions