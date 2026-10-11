import asyncio
import logging

from config.settings import validate_settings
from database.connection import ensure_indexes
from bot.loader import bot, dp
from bot.handlers import start, student_navigation, smart_search, admin_upload
from utils.logger import setup_logging

logger = logging.getLogger(__name__)


async def main() -> None:
    setup_logging()
    validate_settings()
    await ensure_indexes()

    # Registration order matters: admin_upload's file handler has no
    # state filter, so it's registered first to catch admin file
    # sends immediately, before any other router gets a chance.
    dp.include_router(admin_upload.router)
    dp.include_router(start.router)
    dp.include_router(student_navigation.router)
    dp.include_router(smart_search.router)

    logger.info("CampusLib bot starting...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
