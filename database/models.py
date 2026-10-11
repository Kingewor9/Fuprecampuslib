"""
Defines the shape of a 'material' document stored in MongoDB.
Kept as a plain dict builder (no ORM) to match the project's simple,
metadata-only storage model.
"""
from datetime import datetime, timezone


def build_material_document(
    *,
    title: str,
    college: str,
    department: str,
    level: int,
    material_type: str,
    keywords: list[str],
    file_id: str,
    file_kind: str,
    year: int | None = None,
) -> dict:
    """
    Builds a material document ready for insertion into MongoDB.

    Note: per project decision, there is no separate `course_code`
    field — the title itself is the searchable course/material name.

    `file_kind` is Telegram's content type ("document", "photo",
    "video", or "audio") — needed at retrieval time because Telegram
    requires a different send method (send_document/send_photo/etc.)
    depending on how the file was originally uploaded.
    """
    return {
        "title": title,
        "college": college,
        "department": department,
        "level": level,
        "type": material_type,
        "year": year,
        "keywords": keywords,
        "file_id": file_id,
        "file_kind": file_kind,
        "uploaded_at": datetime.now(timezone.utc),
    }
