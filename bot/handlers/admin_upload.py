"""
Admin Upload flow.

The admin (you) sends a file directly to the bot in your DM with it.
The bot forwards that file into the private storage channel (which
generates/preserves the permanent file_id), then walks you through
tagging it: College -> Department -> Level -> Material Type -> Title.
Keywords are auto-generated from the title. On confirm, the metadata
document is written to MongoDB.

Only users in ADMIN_IDS (see config/settings.py) can trigger this flow
— enforced by AdminOnlyMiddleware, registered on this router only.
"""
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.keyboards.admin_menu import (
    admin_colleges_keyboard,
    admin_departments_keyboard,
    admin_levels_keyboard,
    admin_types_keyboard,
    admin_confirm_keyboard,
)
from bot.middlewares.admin_only import AdminOnlyMiddleware
from bot.states.admin_states import AdminUploadStates
from config.settings import STORAGE_CHANNEL_ID
from data.colleges import MATERIAL_TYPES, department_name, college_name
from database.models import build_material_document
from database.queries import insert_material
from search.extractor import extract_keywords

router = Router(name="admin_upload")
router.message.middleware(AdminOnlyMiddleware())
router.callback_query.middleware(AdminOnlyMiddleware())


def _extract_file_info(message: Message) -> tuple[str, str, str] | tuple[None, None, None]:
    """
    Returns (file_id, file_kind, display_name) for whatever kind of
    file was sent. file_kind is one of "document"/"photo"/"video"/"audio"
    and must be stored alongside file_id — Telegram needs it to know
    which send_* method to use when the file is retrieved later.
    """
    if message.document:
        return message.document.file_id, "document", message.document.file_name or "document"
    if message.photo:
        return message.photo[-1].file_id, "photo", "photo"
    if message.video:
        return message.video.file_id, "video", message.video.file_name or "video"
    if message.audio:
        return message.audio.file_id, "audio", message.audio.file_name or "audio"
    return None, None, None


@router.message(Command("upload"))
async def cmd_upload(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(AdminUploadStates.waiting_for_file)
    await message.answer(
        "Send me the file you want to add to CampusLib "
        "(PDF, document, image, etc.)."
    )


@router.message(F.document | F.photo | F.video | F.audio)
async def receive_file(message: Message, state: FSMContext) -> None:
    """
    Any file sent by an admin starts/restarts the upload flow —
    no need to run /upload first.
    """
    file_id, file_kind, display_name = _extract_file_info(message)
    if not file_id:
        await message.answer("I couldn't read that file type. Try sending it again.")
        return

    forwarded = await message.bot.forward_message(
        chat_id=STORAGE_CHANNEL_ID,
        from_chat_id=message.chat.id,
        message_id=message.message_id,
    )
    channel_file_id, channel_file_kind, _ = _extract_file_info(forwarded)
    if not channel_file_id:
        await message.answer(
            "That file was forwarded to storage but I couldn't read its file_id "
            "back. Please try sending it again."
        )
        return

    current_state = await state.get_state()
    current_data = await state.get_data()
    if current_state and current_data.get("file_id"):
        pending_files = current_data.get("pending_files", [])
        pending_files.append(
            {
                "file_id": channel_file_id,
                "file_kind": channel_file_kind,
                "original_name": display_name,
            }
        )
        await state.update_data(pending_files=pending_files)
        await message.answer(
            f"\U0001F4E5 Queued <code>{display_name}</code>. "
            f"It is file {len(pending_files) + 1} in the upload queue."
        )
        return

    await state.clear()
    await state.update_data(
        file_id=channel_file_id,
        file_kind=channel_file_kind,
        original_name=display_name,
        pending_files=[],
    )
    await state.set_state(AdminUploadStates.choosing_college)
    await message.answer(
        f"\u2705 File received and stored (<code>{display_name}</code>).\n\n"
        "Now choose the <b>College</b> to save it under:",
        reply_markup=admin_colleges_keyboard(),
    )


@router.callback_query(AdminUploadStates.choosing_college, F.data.startswith("adm:college:"))
async def choose_college(callback: CallbackQuery, state: FSMContext) -> None:
    college_slug = callback.data.split(":")[2]
    await state.update_data(college=college_slug)
    await state.set_state(AdminUploadStates.choosing_department)
    await callback.message.edit_text(
        f"College: <b>{college_name(college_slug)}</b>\nChoose the Department:",
        reply_markup=admin_departments_keyboard(college_slug),
    )
    await callback.answer()


@router.callback_query(AdminUploadStates.choosing_department, F.data.startswith("adm:dept:"))
async def choose_department(callback: CallbackQuery, state: FSMContext) -> None:
    _, _, college_slug, dept_slug = callback.data.split(":")
    await state.update_data(department=dept_slug)
    await state.set_state(AdminUploadStates.choosing_level)
    await callback.message.edit_text(
        f"Department: <b>{department_name(college_slug, dept_slug)}</b>\n"
        "Choose the Level:",
        reply_markup=admin_levels_keyboard(college_slug, dept_slug),
    )
    await callback.answer()


@router.callback_query(AdminUploadStates.choosing_level, F.data.startswith("adm:level:"))
async def choose_level(callback: CallbackQuery, state: FSMContext) -> None:
    _, _, college_slug, dept_slug, level = callback.data.split(":")
    await state.update_data(level=int(level))
    await state.set_state(AdminUploadStates.choosing_type)
    await callback.message.edit_text(
        f"Level: <b>{level}</b>\nChoose the Material Type:",
        reply_markup=admin_types_keyboard(college_slug, dept_slug, int(level)),
    )
    await callback.answer()


@router.callback_query(AdminUploadStates.choosing_type, F.data.startswith("adm:type:"))
async def choose_type(callback: CallbackQuery, state: FSMContext) -> None:
    _, _, college_slug, dept_slug, level, type_key = callback.data.split(":")
    await state.update_data(type_key=type_key)
    await state.set_state(AdminUploadStates.waiting_for_title)
    await callback.message.edit_text(
        f"Type: <b>{MATERIAL_TYPES[type_key]}</b>\n\n"
        "Now send the <b>title</b> to save this material as, "
        "e.g. <i>GST 101 Past Questions 2022</i>."
    )
    await callback.answer()


@router.message(AdminUploadStates.waiting_for_title, F.text)
async def receive_title(message: Message, state: FSMContext) -> None:
    title = message.text.strip()
    keywords = extract_keywords(title)

    await state.update_data(title=title, keywords=keywords)
    await state.set_state(AdminUploadStates.confirming)

    data = await state.get_data()
    summary = (
        "\U0001F4CB <b>Confirm this material:</b>\n\n"
        f"<b>Title:</b> {title}\n"
        f"<b>College:</b> {college_name(data['college'])}\n"
        f"<b>Department:</b> {department_name(data['college'], data['department'])}\n"
        f"<b>Level:</b> {data['level']}\n"
        f"<b>Type:</b> {MATERIAL_TYPES[data['type_key']]}\n"
        f"<b>Auto keywords:</b> {', '.join(keywords) if keywords else '(none)'}"
    )
    await message.answer(summary, reply_markup=admin_confirm_keyboard())


@router.callback_query(AdminUploadStates.confirming, F.data == "adm:confirm")
async def confirm_save(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    document = build_material_document(
        title=data["title"],
        college=data["college"],
        department=data["department"],
        level=data["level"],
        material_type=data["type_key"],
        keywords=data["keywords"],
        file_id=data["file_id"],
        file_kind=data["file_kind"],
    )
    await insert_material(document)
    pending_files = data.get("pending_files", [])
    if pending_files:
        next_file = pending_files.pop(0)
        await state.clear()
        await state.update_data(**next_file, pending_files=pending_files)
        await state.set_state(AdminUploadStates.choosing_college)
        await callback.message.edit_text(
            f"\u2705 Saved: <b>{data['title']}</b>\n\n"
            f"Next file: <code>{next_file['original_name']}</code>\n"
            "Choose the <b>College</b> to save it under:",
            reply_markup=admin_colleges_keyboard(),
        )
    else:
        await state.clear()
        await callback.message.edit_text(
            f"\u2705 Saved: <b>{data['title']}</b>\n\nSend another file whenever you're ready."
        )
    await callback.answer("Saved!")


@router.callback_query(F.data == "adm:back:title")
async def back_to_title(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminUploadStates.waiting_for_title)
    await callback.message.edit_text("Send the title again:")
    await callback.answer()


@router.callback_query(F.data == "adm:back:college")
async def back_to_college(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminUploadStates.choosing_college)
    await callback.message.edit_text(
        "Choose the <b>College</b> to save it under:",
        reply_markup=admin_colleges_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "adm:back:department")
async def back_to_department(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    college_slug = data["college"]
    await state.set_state(AdminUploadStates.choosing_department)
    await callback.message.edit_text(
        f"College: <b>{college_name(college_slug)}</b>\nChoose the Department:",
        reply_markup=admin_departments_keyboard(college_slug),
    )
    await callback.answer()


@router.callback_query(F.data == "adm:back:level")
async def back_to_level(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    college_slug, dept_slug = data["college"], data["department"]
    await state.set_state(AdminUploadStates.choosing_level)
    await callback.message.edit_text(
        f"Department: <b>{department_name(college_slug, dept_slug)}</b>\n"
        "Choose the Level:",
        reply_markup=admin_levels_keyboard(college_slug, dept_slug),
    )
    await callback.answer()


@router.callback_query(F.data == "adm:cancel")
async def cancel_upload(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("\u274c Upload cancelled.")
    await callback.answer()
