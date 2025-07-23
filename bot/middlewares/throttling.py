from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from core.config import Config
import time
import logging

logger = logging.getLogger(__name__)


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self):
        self.limit = Config.THROTTLE_LIMIT
        self.last_processed = {}
        super().__init__()

    async def __call__(self, handler, event: TelegramObject, data):
        user_id = event.from_user.id
        current_time = time.time()

        if user_id in self.last_processed:
            time_passed = current_time - self.last_processed[user_id]
            if time_passed < self.limit:
                logger.warning(f"Throttling user {user_id}")
                await event.answer("⏳ Слишком много запросов! Пожалуйста, подождите.")
                return

        self.last_processed[user_id] = current_time
        return await handler(event, data)