from aiogram import Router, types
from aiogram.filters import Command
from database import SessionLocal
from database.repositories import UserRepository
from bot.keyboards import static
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

# Создаем роутер для этого модуля
router = Router()


async def start_command(message: types.Message, state: FSMContext):
    await state.clear()
    with SessionLocal() as session:
        user_repo = UserRepository(session)
        user = user_repo.get_user(message.from_user.id)

        if not user:
            # Создание нового пользователя
            user = user_repo.create_user({
                'telegram_id': message.from_user.id,
                'full_name': message.from_user.full_name,
                'username': message.from_user.username,
                'user_type': 'client'
            })

        welcome_text = (
            f"👋 Привет, {message.from_user.full_name}!\n"
            "Я бот для заказа такси с аукционом среди водителей.\n\n"
            "Выберите действие:"
        )

        await message.answer(
            welcome_text,
            reply_markup=static.get_main_kb(user.telegram_id)
        )


router.message.register(start_command, Command('start'))

@router.callback_query(lambda c: c.data == "main_create_order")
async def handle_create_order_callback(callback: CallbackQuery, state: FSMContext):
    from bot.handlers.client.create_order import create_order_start
    await callback.answer("Начинаем создание заказа...")
    await create_order_start(callback.message, state) # Передаем message и state

@router.callback_query(lambda c: c.data == "main_become_driver")
async def handle_become_driver_callback(callback: CallbackQuery, state: FSMContext):
    from bot.handlers.driver.registration import start_registration
    await callback.answer("Переключаемся в режим водителя...")
    await start_registration(callback.message, state) # Передаем message и state

@router.callback_query(lambda c: c.data == "main_help")
async def handle_help_callback(callback: CallbackQuery):
    from bot.handlers.common.feedback import handle_help_button
    await callback.answer("Открываем раздел помощи...")
    await handle_help_button(callback.message) # Передаем message