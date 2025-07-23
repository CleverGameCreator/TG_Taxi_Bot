from aiogram import types
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from database import SessionLocal
from database.repositories import UserRepository


class RoleAccessMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        with SessionLocal() as session:
            user_repo = UserRepository(session)
            user = user_repo.get_user(message.from_user.id)

            if user:
                data['user_role'] = user.user_type
                data['user'] = user
            else:
                data['user_role'] = 'guest'
                data['user'] = None