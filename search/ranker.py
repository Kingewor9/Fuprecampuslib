"""
Ranks a list of material documents against a set of extracted query
keywords. Exact course-code / title matches are prioritized over
partial keyword overlap, per the spec's ranking requirement.
"""


def rank_materials(materials: list[dict], query_keywords: list[str]) -> list[dict]:
    """
    Returns materials sorted by relevance (highest first).
    Materials with no keyword overlap at all are dropped.
    """
    query_set = set(query_keywords)
    numeric_query_keywords = {
        keyword for keyword in query_set if keyword.isdigit()
    }
    scored = []

    for material in materials:
        material_keywords = set(material.get("keywords", []))
        overlap = query_set & material_keywords

        if not overlap or not numeric_query_keywords.issubset(material_keywords):
            continue

        # Exact match: every query keyword is present in the material's
        # keyword set (e.g. full course code + type matched exactly).
        is_exact = query_set.issubset(material_keywords)

        score = len(overlap) + (100 if is_exact else 0)
        scored.append((score, material))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [material for _, material in scored]
