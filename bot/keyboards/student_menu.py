"""
Inline keyboards for the student Menu Navigation flow (Method 1).

Callback data convention: "nav:<action>:<...args>"
"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.colleges import COLLEGES, MATERIAL_TYPES, get_levels


def colleges_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for slug, college in COLLEGES.items():
        builder.button(text=college["name"], callback_data=f"nav:college:{slug}")
    builder.adjust(1)
    return builder.as_markup()


def departments_keyboard(college_slug: str) -> InlineKeyboardMarkup:
    college = COLLEGES[college_slug]
    builder = InlineKeyboardBuilder()
    for slug, dept in college["departments"].items():
        builder.button(
            text=dept["name"], callback_data=f"nav:dept:{college_slug}:{slug}"
        )
    builder.button(text="\u2b05\ufe0f Back", callback_data="nav:back:college")
    builder.adjust(1)
    return builder.as_markup()


def levels_keyboard(college_slug: str, dept_slug: str) -> InlineKeyboardMarkup:
    levels = get_levels(college_slug, dept_slug)
    builder = InlineKeyboardBuilder()
    for level in levels:
        builder.button(
            text=f"{level} Level",
            callback_data=f"nav:level:{college_slug}:{dept_slug}:{level}",
        )
    builder.button(text="\u2b05\ufe0f Back", callback_data="nav:back:department")
    builder.adjust(2)
    return builder.as_markup()


def material_types_keyboard(
    college_slug: str, dept_slug: str, level: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for type_key, label in MATERIAL_TYPES.items():
        builder.button(
            text=label,
            callback_data=f"nav:type:{college_slug}:{dept_slug}:{level}:{type_key}",
        )
    builder.button(text="\u2b05\ufe0f Back", callback_data="nav:back:level")
    builder.adjust(1)
    return builder.as_markup()


def results_pagination_keyboard(
    current_page: int, total_pages: int
) -> InlineKeyboardMarkup | None:
    if total_pages <= 1:
        builder = InlineKeyboardBuilder()
        builder.button(text="\u2b05\ufe0f Back", callback_data="nav:back:type")
        return builder.as_markup()

    builder = InlineKeyboardBuilder()
    row = []
    if current_page > 0:
        row.append(
            InlineKeyboardButton(text="\u25c0\ufe0f Prev", callback_data="nav:page:prev")
        )
    row.append(
        InlineKeyboardButton(
            text=f"{current_page + 1}/{total_pages}", callback_data="nav:noop"
        )
    )
    if current_page < total_pages - 1:
        row.append(
            InlineKeyboardButton(text="Next \u25b6\ufe0f", callback_data="nav:page:next")
        )
    builder.row(*row)
    builder.row(
        InlineKeyboardButton(text="\u2b05\ufe0f Back", callback_data="nav:back:type")
    )
    return builder.as_markup()


def search_results_pagination_keyboard(
    current_page: int, total_pages: int
) -> InlineKeyboardMarkup | None:
    if total_pages <= 1:
        return None

    builder = InlineKeyboardBuilder()
    row = []
    if current_page > 0:
        row.append(
            InlineKeyboardButton(
                text="\u25c0\ufe0f Prev", callback_data="search:page:prev"
            )
        )
    row.append(
        InlineKeyboardButton(
            text=f"{current_page + 1}/{total_pages}", callback_data="search:noop"
        )
    )
    if current_page < total_pages - 1:
        row.append(
            InlineKeyboardButton(
                text="Next \u25b6\ufe0f", callback_data="search:page:next"
            )
        )
    builder.row(*row)
    return builder.as_markup()
