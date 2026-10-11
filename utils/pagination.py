"""
Simple pagination helper for splitting long result lists into pages,
used by both student navigation results and search results.
"""

PAGE_SIZE = 5


def paginate(items: list, page: int) -> tuple[list, int, int]:
    """
    Returns (items_for_this_page, current_page, total_pages).
    `page` is 0-indexed.
    """
    total_pages = max(1, (len(items) + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(0, min(page, total_pages - 1))
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    return items[start:end], page, total_pages
