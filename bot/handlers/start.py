"""
/start - welcome message for new users, explains what the bot does.
/menu  - entry point into Menu Navigation (Method 1).
"""
from html import escape

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.student_menu import colleges_keyboard, departments_keyboard
from bot.states.live_lecture_states import LiveLectureStates
from bot.states.navigation_states import NavigationStates
from data.colleges import college_name, department_name
from data.live_lecture_channels import LIVE_LECTURE_CHANNELS

router = Router(name="start")

WELCOME_MESSAGE = (
    "\U0001F4DA <b>Welcome to CampusLib!</b>\n\n"
    "CampusLib is your school's digital library, right here on Telegram. "
    "Find lecture notes, past questions, and other study materials in seconds "
    "— no groups to search through, no random forwarded files.\n\n"
    "Here's how to get materials:\n\n"
    "\U0001F538 <b>/menu</b> — Browse step-by-step: pick your College, "
    "Department, Level, and the type of material you need.\n\n"
    "\U0001F538 <b>/search</b> — Just type what you're looking for, e.g. "
    "<i>\"GST 101 past questions\"</i>, and CampusLib finds it instantly.\n\n"
    "Let's get you your materials \u2014 tap a command below to begin."
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(WELCOME_MESSAGE)


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext) -> None:
    await state.set_state(NavigationStates.choosing_college)
    await message.answer(
        "Choose your <b>College</b> to begin:",
        reply_markup=colleges_keyboard(),
    )


@router.message(Command("lectures"))
async def cmd_lectures(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(LiveLectureStates.choosing_college)
    await message.answer(
        "Choose your <b>College</b> for live lectures:",
        reply_markup=colleges_keyboard(),
    )


@router.callback_query(
    LiveLectureStates.choosing_college, F.data.startswith("nav:college:")
)
async def choose_lecture_college(
    callback: CallbackQuery, state: FSMContext
) -> None:
    college_slug = callback.data.split(":")[2]
    await state.update_data(lecture_college=college_slug)
    await state.set_state(LiveLectureStates.choosing_department)
    await callback.message.edit_text(
        f"College: <b>{college_name(college_slug)}</b>\n"
        "Now choose your Department:",
        reply_markup=departments_keyboard(college_slug),
    )
    await callback.answer()


@router.callback_query(
    LiveLectureStates.choosing_department, F.data.startswith("nav:dept:")
)
async def choose_lecture_department(callback: CallbackQuery, state: FSMContext) -> None:
    _, _, college_slug, dept_slug = callback.data.split(":")
    channel_url = LIVE_LECTURE_CHANNELS.get(college_slug, {}).get(dept_slug, "")
    dept_label = department_name(college_slug, dept_slug)

    if channel_url:
        response = (
            f"Join the <b>{dept_label} Live Lectures</b> Telegram channel to "
            "receive live lectures and stay up to date:\n\n"
            f'<a href="{escape(channel_url, quote=True)}">Join the channel</a>'
        )
    else:
        response = (
            f"The Telegram live lectures channel for <b>{dept_label}</b> "
            "has not been configured yet. Please check back soon."
        )

    await state.clear()
    await callback.message.edit_text(response)
    await callback.answer()


@router.callback_query(
    LiveLectureStates.choosing_department, F.data == "nav:back:college"
)
async def back_to_lecture_college(
    callback: CallbackQuery, state: FSMContext
) -> None:
    await state.set_state(LiveLectureStates.choosing_college)
    await callback.message.edit_text(
        "Choose your <b>College</b> for live lectures:",
        reply_markup=colleges_keyboard(),
    )
    await callback.answer()
