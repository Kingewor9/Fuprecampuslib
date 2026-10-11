"""
Loads environment variables and exposes them as constants
used throughout the project.
"""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "campuslib")

STORAGE_CHANNEL_ID = os.getenv("STORAGE_CHANNEL_ID")
if STORAGE_CHANNEL_ID:
    STORAGE_CHANNEL_ID = int(STORAGE_CHANNEL_ID)

_admin_ids_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = {
    int(uid.strip())
    for uid in _admin_ids_raw.split(",")
    if uid.strip().isdigit()
}

# Basic startup validation so misconfiguration fails loudly, not silently.
def validate_settings() -> None:
    missing = []
    if not BOT_TOKEN:
        missing.append("BOT_TOKEN")
    if not STORAGE_CHANNEL_ID:
        missing.append("STORAGE_CHANNEL_ID")
    if not ADMIN_IDS:
        missing.append("ADMIN_IDS")
    if missing:
        raise RuntimeError(
            f"Missing required .env values: {', '.join(missing)}"
        )
