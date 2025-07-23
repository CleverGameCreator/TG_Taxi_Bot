from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from bot.states import DriverBidding
from services.auction import process_bid
from utils.formatters import format_price
from database import SessionLocal
from database.repositories import OrderRepository, BidRepository
from bot.keyboards.inline import auction
import logging

logger = logging.getLogger(__name__)

# Создаем роутер для этого модуля
router = Router()


async def start_bidding(
        callback: types.CallbackQuery,
        callback_data: dict,
        state: FSMContext
):
    order_id = callback_data['order_id']
    action = callback_data['action']

    if action == "create":
        await state.set_state(DriverBidding.PRICE)
        await state.update_data(order_id=order_id)
        await callback.message.answer("💰 Введите вашу цену:")
    elif action == "refresh":
        with SessionLocal() as session:
            try:
                order_repo = OrderRepository(session)
                bid_repo = BidRepository(session)

                order = order_repo.get_order(order_id)
                bids = bid_repo.get_bids_for_order(order_id)
                lowest_bid = bids[0] if bids else None

                text = "Актуальная информация по заказу:\n"
                if lowest_bid:
                    text += f"Текущая минимальная ставка: {format_price(lowest_bid.price)}"
                else:
                    text += "Ставок пока нет"

                await callback.message.answer(text)
            except Exception as e:
                logger.error(f"Error refreshing order: {e}")
                await callback.answer("Ошибка при обновлении информации")


async def process_bid_price(message: types.Message, state: FSMContext):
    try:
        price = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите число")
        return

    data = await state.get_data()
    order_id = data['order_id']

    try:
        success = process_bid(
            driver_id=message.from_user.id,
            order_id=order_id,
            price=price
        )

        if success:
            await message.answer(f"✅ Ваша ставка {format_price(price)} принята!")
        else:
            await message.answer("❌ Не удалось принять ставку. Возможно, аукцион завершен.")
    except Exception as e:
        logger.error(f"Bid processing error: {e}")
        await message.answer("❌ Произошла ошибка при обработке ставки")

    await state.clear()


def register_handlers(router_instance: Router):
    """Регистрирует обработчики для этого модуля"""
    router_instance.callback_query.register(
        start_bidding,
        auction.bid_cb.filter()
    )
    router_instance.message.register(
        process_bid_price,
        DriverBidding.PRICE
    )