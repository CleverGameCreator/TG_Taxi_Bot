from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from database import SessionLocal
from database.repositories import OrderRepository
from services.auction import complete_auction
from services.notification import notify_order_accepted
from bot.keyboards.inline import auction
import logging

logger = logging.getLogger(__name__)

# Создаем роутер для этого модуля
router = Router()


async def select_driver(callback: types.CallbackQuery, callback_data: dict):
    driver_id = int(callback_data['driver_id'])
    order_id = callback_data['order_id']

    try:
        with SessionLocal() as session:
            # Завершаем аукцион и назначаем водителя
            order = complete_auction(order_id, driver_id)
            await callback.message.answer(
                f"✅ Вы выбрали водителя для заказа #{order_id}!\n"
                "Ожидайте, когда водитель подтвердит заказ"
            )
            await notify_order_accepted(order_id, callback.bot)
    except ValueError as e:
        logger.error(f"Validation error selecting driver: {e}")
        await callback.answer(str(e))
    except Exception as e:
        logger.error(f"Error selecting driver: {e}")
        await callback.answer("Ошибка при выборе водителя. Попробуйте позже.")


router.callback_query.register(
    select_driver,
    auction.driver_cb.filter(lambda c: c.action == "select") # Исправлено использование фильтра CallbackData
)