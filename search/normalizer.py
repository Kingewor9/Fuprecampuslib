"""
Maps variant words/phrases onto a single canonical keyword so that
"pq", "past question", "past questions" etc. all match the same thing.
"""

# Canonical keyword -> list of variant phrases (lowercase, no punctuation)
NORMALIZATION_GROUPS = {
    "past_question": ["pq", "past", "past question", "past questions", "pastquestion"],
    "lecture_note": ["notes", "note", "lecture notes", "lecture note", "handout", "handouts"],
}

# Flatten into a direct lookup: variant -> canonical
_VARIANT_TO_CANONICAL = {}
for canonical, variants in NORMALIZATION_GROUPS.items():
    for variant in variants:
        _VARIANT_TO_CANONICAL[variant] = canonical
    # a canonical keyword should also map to itself
    _VARIANT_TO_CANONICAL[canonical] = canonical


def normalize_word(word: str) -> str:
    """
    Normalize a single word/token against known variants.
    Falls back to the original (lowercased) word if no mapping exists.
    """
    word = word.lower().strip()
    return _VARIANT_TO_CANONICAL.get(word, word)


def normalize_phrase(phrase: str) -> str:
    """
    Normalize a full phrase (e.g. 'past questions') against known variants.
    Checked before falling back to per-word normalization, since some
    mappings only make sense as a full phrase (e.g. 'lecture notes').
    """
    phrase = phrase.lower().strip()
    return _VARIANT_TO_CANONICAL.get(phrase, phrase)
