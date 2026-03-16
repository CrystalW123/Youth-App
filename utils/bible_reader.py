import json
import os
import re


def parse_reference(reference: str):
    """
    Supports:
    - John 3:16
    - Ephesians 1:3
    - Philippians 4:6-7
    - 1 John 4:8
    """
    reference = reference.strip()

    # Match range: Book 4:6-7
    range_match = re.match(r"^(.*?)\s+(\d+):(\d+)-(\d+)$", reference)
    if range_match:
        book = range_match.group(1).strip()
        chapter = int(range_match.group(2))
        start_verse = int(range_match.group(3))
        end_verse = int(range_match.group(4))
        return book, chapter, start_verse, end_verse

    # Match single verse: Book 4:6
    single_match = re.match(r"^(.*?)\s+(\d+):(\d+)$", reference)
    if single_match:
        book = single_match.group(1).strip()
        chapter = int(single_match.group(2))
        verse = int(single_match.group(3))
        return book, chapter, verse, verse

    raise ValueError(f"Invalid reference format: {reference}")


def get_verse_text(reference: str, bible_folder: str = "data/bible/json"):
    book, chapter, start_verse, end_verse = parse_reference(reference)

    file_name = f"{book.lower().replace(' ', '')}.json"
    file_path = os.path.join(bible_folder, file_name)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Book file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        book_data = json.load(file)

    verses_found = {}

    for item in book_data:
        if (
            item.get("type") in ["paragraph text", "line text"]
            and item.get("chapterNumber") == chapter
            and start_verse <= item.get("verseNumber") <= end_verse
        ):
            verse_number = item.get("verseNumber")
            verse_text = item.get("value", "").strip()

            if verse_number not in verses_found:
                verses_found[verse_number] = []

            verses_found[verse_number].append(verse_text)

    if not verses_found:
        raise ValueError(
            f"Verse not found in {file_name}: {chapter}:{start_verse}-{end_verse}"
        )

    formatted_verses = []
    for verse_number in range(start_verse, end_verse + 1):
        if verse_number in verses_found:
            joined_text = " ".join(verses_found[verse_number]).replace("  ", " ").strip()
            formatted_verses.append(f"{verse_number}. {joined_text}")

    return "\n\n".join(formatted_verses)

