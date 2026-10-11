"""
Inline keyboards for the Admin Upload flow.

Callback data convention: "adm:<action>:<...args>"
"""
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.colleges import COLLEGES, MATERIAL_TYPES, get_levels


def admin_colleges_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for slug, college in COLLEGES.items():
        builder.button(text=college["name"], callback_data=f"adm:college:{slug}")
    builder.button(text="\u274c Cancel", callback_data="adm:cancel")
    builder.adjust(1)
    return builder.as_markup()


def admin_departments_keyboard(college_slug: str) -> InlineKeyboardMarkup:
    college = COLLEGES[college_slug]
    builder = InlineKeyboardBuilder()
    for slug, dept in college["departments"].items():
        builder.button(
            text=dept["name"], callback_data=f"adm:dept:{college_slug}:{slug}"
        )
    builder.button(text="\u2b05\ufe0f Back", callback_data="adm:back:college")
    builder.button(text="\u274c Cancel", callback_data="adm:cancel")
    builder.adjust(1)
    return builder.as_markup()


def admin_levels_keyboard(college_slug: str, dept_slug: str) -> InlineKeyboardMarkup:
    levels = get_levels(college_slug, dept_slug)
    builder = InlineKeyboardBuilder()
    for level in levels:
        builder.button(
            text=f"{level} Level",
            callback_data=f"adm:level:{college_slug}:{dept_slug}:{level}",
        )
    builder.button(text="\u2b05\ufe0f Back", callback_data="adm:back:department")
    builder.button(text="\u274c Cancel", callback_data="adm:cancel")
    builder.adjust(2)
    return builder.as_markup()


def admin_types_keyboard(
    college_slug: str, dept_slug: str, level: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for type_key, label in MATERIAL_TYPES.items():
        builder.button(
            text=label,
            callback_data=f"adm:type:{college_slug}:{dept_slug}:{level}:{type_key}",
        )
    builder.button(text="\u2b05\ufe0f Back", callback_data="adm:back:level")
    builder.button(text="\u274c Cancel", callback_data="adm:cancel")
    builder.adjust(1)
    return builder.as_markup()


def admin_confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="\u2705 Save", callback_data="adm:confirm")
    builder.button(text="\u270f\ufe0f Retype title", callback_data="adm:back:title")
    builder.button(text="\u274c Cancel", callback_data="adm:cancel")
    builder.adjust(1)
    return builder.as_markup()
