"""
Telegram requires a different send method depending on how a file was
originally uploaded (send_document / send_photo / send_video /
send_audio). Materials store which kind they are (`file_kind`) so
retrieval can call the right one instead of assuming everything is a
document.
"""
from aiogram.types import Message


async def send_material(message: Message, material: dict) -> None:
    file_id = material["file_id"]
    caption = f"\U0001F4C4 {material['title']}"
    kind = material.get("file_kind")

    # Older records do not have file_kind. Telegram file paths preserve the
    # original media category, so use that metadata before choosing a method.
    if not kind:
        telegram_file = await message.bot.get_file(file_id)
        file_path = telegram_file.file_path or ""
        if file_path.startswith("photos/"):
            kind = "photo"
        elif file_path.startswith("videos/"):
            kind = "video"
        elif file_path.startswith("audio/"):
            kind = "audio"
        else:
            kind = "document"

    if kind == "photo":
        await message.answer_photo(photo=file_id, caption=caption)
    elif kind == "video":
        await message.answer_video(video=file_id, caption=caption)
    elif kind == "audio":
        await message.answer_audio(audio=file_id, caption=caption)
    else:
        await message.answer_document(document=file_id, caption=caption)
