"""
MongoDB connection using Motor (async driver).
Import `db` anywhere you need to run a query.
"""
from motor.motor_asyncio import AsyncIOMotorClient

from config.settings import MONGO_URI, MONGO_DB_NAME

_client = AsyncIOMotorClient(MONGO_URI)
db = _client[MONGO_DB_NAME]

materials_collection = db["materials"]


async def ensure_indexes() -> None:
    """
    Creates indexes that make search fast. Call once at startup.
    """
    await materials_collection.create_index("keywords")
    await materials_collection.create_index("college")
    await materials_collection.create_index("department")
    await materials_collection.create_index("level")
    await materials_collection.create_index("type")
