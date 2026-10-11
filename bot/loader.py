"""
Creates the single Bot and Dispatcher instances used across the app.
"""
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation

from config.settings import BOT_TOKEN

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

# MemoryStorage is fine for a single-instance final-year project.
# Swap for RedisStorage later if the bot needs to scale horizontally.
dp = Dispatcher(
    storage=MemoryStorage(),
    events_isolation=SimpleEventIsolation(),
)
