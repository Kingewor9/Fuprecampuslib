"""
Menu Navigation flow (Method 1): College -> Department -> Level ->
Material Type -> Results.

Callback data convention: "nav:<action>:<...args>"
"""
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards.student_menu import (
    colleges_keyboard,
    departments_keyboard,
    levels_keyboard,
    material_types_keyboard,
    results_pagination_keyboard,
)
from bot.states.navigation_states import NavigationStates
from data.colleges import MATERIAL_TYPES, department_name, college_name
from database.queries import get_materials_by_menu_path
from utils.file_sender import send_material
from utils.pagination import paginate

router = Router(name="student_navigation")


@router.callback_query(NavigationStates.choosing_college, F.data.startswith("nav:college:"))
async def choose_college(callback: CallbackQuery, state: FSMContext) -> None:
    college_slug = callback.data.split(":")[2]
    await state.update_data(college=college_slug)
    await state.set_state(NavigationStates.choosing_department)
    await callback.message.edit_text(
        f"College: <b>{college_name(college_slug)}</b>\nNow choose your Department:",
        reply_markup=departments_keyboard(college_slug),
    )
    await callback.answer()


@router.callback_query(NavigationStates.choosing_department, F.data.startswith("nav:dept:"))
async def choose_department(callback: CallbackQuery, state: FSMContext) -> None:
    _, _, college_slug, dept_slug = callback.data.split(":")
    await state.update_data(department=dept_slug)
    await state.set_state(NavigationStates.choosing_level)
    await callback.message.edit_text(
        f"Department: <b>{department_name(college_slug, dept_slug)}</b>\n"
        "Now choose your Level:",
        reply_markup=levels_keyboard(college_slug, dept_slug),
    )
    await callback.answer()


@router.callback_query(NavigationStates.choosing_level, F.data.startswith("nav:level:"))
async def choose_level(callback: CallbackQuery, state: FSMContext) -> None:
    _, _, college_slug, dept_slug, level = callback.data.split(":")
    await state.update_data(level=int(level))
    await state.set_state(NavigationStates.choosing_type)
    await callback.message.edit_text(
        f"Level: <b>{level}</b>\nWhat type of material do you need?",
        reply_markup=material_types_keyboard(college_slug, dept_slug, int(level)),
    )
    await callback.answer()


@router.callback_query(NavigationStates.choosing_type, F.data.startswith("nav:type:"))
async def choose_type(callback: CallbackQuery, state: FSMContext) -> None:
    _, _, college_slug, dept_slug, level, type_key = callback.data.split(":")
    materials = await get_materials_by_menu_path(
        college=college_slug,
        department=dept_slug,
        level=int(level),
        material_type=type_key,
    )

    if not materials:
        await state.set_state(NavigationStates.choosing_type)
        await callback.message.edit_text(
            "No materials found for that selection yet. Check back later, "
            "or try a different Level / Material Type.",
            reply_markup=material_types_keyboard(college_slug, dept_slug, int(level)),
        )
        await callback.answer()
        return

    await state.update_data(
        results=materials,
        page=0,
        type_key=type_key,
    )
    await state.set_state(NavigationStates.viewing_results)
    await callback.message.edit_text(
        f"Found <b>{len(materials)}</b> matching {MATERIAL_TYPES[type_key]}:"
    )
    await _send_results_page(callback, state, page=0)
    await callback.answer()


@router.callback_query(NavigationStates.viewing_results, F.data.startswith("nav:page:"))
async def paginate_results(callback: CallbackQuery, state: FSMContext) -> None:
    direction = callback.data.split(":")[2]
    data = await state.get_data()
    current_page = data.get("page", 0)
    new_page = current_page + 1 if direction == "next" else current_page - 1
    await _send_results_page(callback, state, page=new_page)
    await callback.answer()


@router.callback_query(F.data == "nav:noop")
async def noop(callback: CallbackQuery) -> None:
    await callback.answer()


async def _send_results_page(callback: CallbackQuery, state: FSMContext, page: int) -> None:
    data = await state.get_data()
    materials = data.get("results", [])
    page_items, current_page, total_pages = paginate(materials, page)
    await state.update_data(page=current_page)

    for material in page_items:
        await send_material(callback.message, material)

    await callback.message.answer(
        "Use the buttons below for more results or to go back.",
        reply_markup=results_pagination_keyboard(current_page, total_pages),
    )


# ---- Back navigation ----

@router.callback_query(F.data == "nav:back:college")
async def back_to_college(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(NavigationStates.choosing_college)
    await callback.message.edit_text(
        "Choose your <b>College</b> to begin:", reply_markup=colleges_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "nav:back:department")
async def back_to_department(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    college_slug = data["college"]
    await state.set_state(NavigationStates.choosing_department)
    await callback.message.edit_text(
        f"College: <b>{college_name(college_slug)}</b>\nNow choose your Department:",
        reply_markup=departments_keyboard(college_slug),
    )
    await callback.answer()


@router.callback_query(F.data == "nav:back:level")
async def back_to_level(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    college_slug, dept_slug = data["college"], data["department"]
    await state.set_state(NavigationStates.choosing_level)
    await callback.message.edit_text(
        f"Department: <b>{department_name(college_slug, dept_slug)}</b>\n"
        "Now choose your Level:",
        reply_markup=levels_keyboard(college_slug, dept_slug),
    )
    await callback.answer()


@router.callback_query(F.data == "nav:back:type")
async def back_to_type(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    college_slug, dept_slug, level = data["college"], data["department"], data["level"]
    await state.set_state(NavigationStates.choosing_type)
    await callback.message.edit_text(
        f"Level: <b>{level}</b>\nWhat type of material do you need?",
        reply_markup=material_types_keyboard(college_slug, dept_slug, level),
    )
    await callback.answer()
