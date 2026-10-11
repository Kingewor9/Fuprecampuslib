"""
Extracts and normalizes keywords from free text.

Used in two places:
1. Admin upload flow — auto-generate keywords from a material's title.
2. Smart Search — extract keywords from a student's search query.
"""
import re

from search.normalizer import normalize_phrase, normalize_word

# Common filler words that add no search value.
STOPWORDS = {"a", "an", "the", "for", "of", "and", "in", "on", "to"}

# Matches a course-code-like token, e.g. "GST101", "MEE 201" (letters then digits)
COURSE_CODE_PATTERN = re.compile(r"\b([a-zA-Z]{2,6})\s?-?\s?(\d{3})\b")

# Two-word phrases that should be checked before single-word normalization
_TWO_WORD_PHRASES = ["past questions", "past question", "lecture notes", "lecture note"]


def extract_course_codes(text: str) -> list[str]:
    """
    Finds course-code-like patterns (e.g. 'GST 101', 'MEE201') and
    returns them normalized as 'GST 101', 'MEE 201', etc.
    """
    matches = COURSE_CODE_PATTERN.findall(text)
    return [f"{letters.upper()} {digits}" for letters, digits in matches]


def extract_keywords(text: str) -> list[str]:
    """
    Tokenizes free text into a deduplicated list of normalized keywords.
    Course codes are kept together (e.g. 'gst101' -> 'gst', '101' as
    separate tokens too, so either matches).
    """
    text = text.lower().strip()
    keywords: set[str] = set()

    # Capture course codes as combined + split tokens, then strip the
    # matched span from the text so it isn't also tokenized whole
    # (e.g. "gst101" alongside "gst" + "101").
    remaining_text = text
    for match in COURSE_CODE_PATTERN.finditer(text):
        letters, digits = match.group(1), match.group(2)
        keywords.add(letters.lower())
        keywords.add(digits)
        remaining_text = remaining_text.replace(match.group(0), " ")

    # Normalize known two-word phrases first, then remove them from text
    # so they aren't re-tokenized as separate single words.
    for phrase in _TWO_WORD_PHRASES:
        if phrase in remaining_text:
            keywords.add(normalize_phrase(phrase))
            remaining_text = remaining_text.replace(phrase, " ")

    # Tokenize what's left into individual words
    tokens = re.findall(r"[a-zA-Z0-9]+", remaining_text)
    for token in tokens:
        if token in STOPWORDS:
            continue
        keywords.add(normalize_word(token))

    return sorted(keywords)
