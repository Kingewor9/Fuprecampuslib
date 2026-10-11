"""
All MongoDB read/write operations live here so handlers never touch
the collection directly.
"""
from database.connection import materials_collection


async def insert_material(document: dict) -> str:
    result = await materials_collection.insert_one(document)
    return str(result.inserted_id)


async def get_materials_by_menu_path(
    college: str, department: str, level: int, material_type: str
) -> list[dict]:
    """
    Used by the Menu Navigation flow (Method 1) — exact filter match,
    no ranking needed since the user already narrowed everything down
    via buttons.
    """
    cursor = materials_collection.find(
        {
            "college": college,
            "department": department,
            "level": level,
            "type": material_type,
        }
    )
    return await cursor.to_list(length=None)


async def search_materials_by_keywords(keywords: list[str]) -> list[dict]:
    """
    Used by Smart Search (Method 2) — broad candidate fetch, ranking
    happens afterwards in search/ranker.py.
    """
    if not keywords:
        return []
    cursor = materials_collection.find({"keywords": {"$in": keywords}})
    return await cursor.to_list(length=None)


async def count_materials() -> int:
    return await materials_collection.count_documents({})
