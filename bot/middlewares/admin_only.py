"""
Blocks any update from reaching admin handlers unless it comes from
a Telegram user ID listed in ADMIN_IDS.
"""
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from config.settings import ADMIN_IDS


class AdminOnlyMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None or user.id not in ADMIN_IDS:
            # Silently ignore — a non-admin should never see admin flow
            # feedback, since /upload isn't advertised to students.
            return None
        return await handler(event, data)
