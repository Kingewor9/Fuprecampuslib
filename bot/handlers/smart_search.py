"""
Smart Search flow (Method 2): free-text keyword search, no AI —
structured keyword extraction + normalization + ranking.
"""
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.keyboards.student_menu import search_results_pagination_keyboard
from bot.states.search_states import SearchStates
from database.queries import search_materials_by_keywords
from search.extractor import extract_keywords
from search.ranker import rank_materials
from utils.file_sender import send_material
from utils.pagination import PAGE_SIZE, paginate

router = Router(name="smart_search")


@router.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext) -> None:
    await state.set_state(SearchStates.waiting_for_query)
    await message.answer(
        "Send a course code or keyword, e.g. <i>GST 101 past questions</i>"
    )


@router.message(SearchStates.waiting_for_query, F.text)
async def handle_search_query(message: Message, state: FSMContext) -> None:
    query_keywords = extract_keywords(message.text)

    if not query_keywords:
        await message.answer(
            "I couldn't pick out anything to search for. Try including a "
            "course code or a word like 'notes' or 'past questions'."
        )
        return

    candidates = await search_materials_by_keywords(query_keywords)
    results = rank_materials(candidates, query_keywords)

    if not results:
        await message.answer(
            f"No materials found for \u201c{message.text}\u201d. "
            "Try a different keyword or use /menu to browse instead."
        )
        return

    await state.update_data(results=results, page=0)
    await state.set_state(SearchStates.viewing_results)
    await message.answer(f"Results for \u201c{message.text}\u201d ({len(results)} found):")
    await _send_search_results_page(message, state, page=0)


@router.callback_query(SearchStates.viewing_results, F.data.startswith("search:page:"))
async def paginate_search_results(callback: CallbackQuery, state: FSMContext) -> None:
    direction = callback.data.split(":")[2]
    data = await state.get_data()
    current_page = data.get("page", 0)
    new_page = current_page + 1 if direction == "next" else current_page - 1
    await _send_search_results_page(callback.message, state, page=new_page)
    await callback.answer()


@router.callback_query(SearchStates.viewing_results, F.data == "search:noop")
async def search_page_number(callback: CallbackQuery) -> None:
    await callback.answer()


async def _send_search_results_page(
    message: Message, state: FSMContext, page: int
) -> None:
    data = await state.get_data()
    results = data.get("results", [])
    page_items, current_page, total_pages = paginate(results, page)
    await state.update_data(page=current_page)

    for material in page_items:
        await send_material(message, material)

    first_result = current_page * PAGE_SIZE + 1
    last_result = first_result + len(page_items) - 1
    await message.answer(
        f"Showing results {first_result}-{last_result} of {len(results)}.",
        reply_markup=search_results_pagination_keyboard(current_page, total_pages),
    )
