from aiogram import types, Dispatcher, F, Router, Bot
from aiogram.fsm.context import FSMContext
from bot.states import OrderCreation
from bot.keyboards import static, inline
from database.repositories import OrderRepository
from services.notification import notify_drivers_about_order
from utils.formatters import format_order
from core.config import Config
import uuid
from database import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.filters.callback_data import CallbackData
from typing import Optional
from database.models import Order
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.deep_linking import create_start_link
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message


# Создаем роутер для этого модуля
router = Router()


async def create_order_start(message: types.Message, state: FSMContext):
    await state.set_state(OrderCreation.START_POINT)
    await message.answer(
        "📍 Введите адрес отправления (точка А):",
        reply_markup=static.get_cancel_kb()
    )


async def process_start_point(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data = data or {}
    data['start_point'] = message.text
    await state.set_data(data) # Обновляем данные

    await state.set_state(OrderCreation.END_POINT)
    await message.answer("🏁 Введите адрес назначения (точка Б):")


async def process_end_point(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data = data or {}
    data['end_point'] = message.text
    await state.set_data(data) # Обновляем данные

    await state.set_state(OrderCreation.TIME)
    await message.answer("⏰ Введите время поездки (в формате ЧЧ:ММ):")


async def process_time(message: types.Message, state: FSMContext):
    # Простая валидация времени
    if not message.text.replace(':', '').isdigit() or len(message.text) != 5:
        await message.answer("Пожалуйста, введите время в формате ЧЧ:ММ (например 14:30)")
        return

    data = await state.get_data()
    data = data or {}
    data['time'] = message.text
    await state.set_data(data) # Обновляем данные

    await state.set_state(OrderCreation.PRICE)
    await message.answer("💰 Введите максимальную цену (руб):")


async def process_price(message: types.Message, state: FSMContext):
    try:
        price = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите число")
        return

    data = await state.get_data()
    data = data or {}
    data['price'] = price
    await state.set_data(data) # Обновляем данные

    await state.set_state(OrderCreation.CONFIRM)
    await message.answer(
        format_order(data),
        reply_markup=inline.get_order_confirmation_kb()
    )


@router.callback_query(lambda c: c.data == "order_confirm", OrderCreation.CONFIRM)
async def confirm_order(callback: types.CallbackQuery, state: FSMContext, bot: Bot): # Изменена сигнатура, убран order_repo
    data = await state.get_data()

    # Получаем сессию и репозиторий внутри функции
    session = SessionLocal() # Создаем сессию явно
    try:
        order_repo = OrderRepository(session)

        # Создаем объект Order
        order_data = {
            'id': str(uuid.uuid4()), # Генерируем UUID для id
            'client_id': callback.from_user.id,
            'start_point': data.get('start_point'),
            'end_point': data.get('end_point'),
            'price': data.get('price'),
            'time': data.get('time'),
            'status': 'active'
        }
        order = Order(**order_data) # Создаем объект Order напрямую
        order_repo.session.add(order) # Добавляем объект в сессию репозитория
        order_repo.session.commit() # Коммитим изменения
        order_repo.session.refresh(order) # Обновляем объект, чтобы он был присоединен к сессии

    finally:
        session.close() # Закрываем сессию в блоке finally

    await callback.message.answer("Заказ успешно создан!")
    await state.clear()

    # Удаляем inline клавиатуру после подтверждения
    await callback.message.edit_reply_markup(reply_markup=None)

    # Уведомляем водителей о новом заказе
    await notify_drivers_about_order(order.id, bot) # Передаем bot

    await callback.message.answer(
        "✅ Заказ создан! Ожидайте предложений от водителей",
        reply_markup=static.get_main_kb(callback.from_user.id)
    )
    await callback.answer("Заказ подтвержден!")


router.message.register(process_start_point, OrderCreation.START_POINT)
router.message.register(process_end_point, OrderCreation.END_POINT)
router.message.register(process_time, OrderCreation.TIME)
router.message.register(process_price, OrderCreation.PRICE)