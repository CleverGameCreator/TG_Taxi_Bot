from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from bot.states import DriverBidding
from services.auction import process_bid, complete_auction
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
    elif action == "cancel":
        # Отмена ставки водителем
        with SessionLocal() as session:
            try:
                bid_repo = BidRepository(session)
                # Удаляем ставку водителя по этому заказу
                bid_repo.delete_driver_bid(order_id, callback.from_user.id)
                await callback.answer("Ваша ставка отменена")
                await callback.message.answer("✅ Ваша ставка по этому заказу отменена")
            except Exception as e:
                logger.error(f"Error canceling bid: {e}")
                await callback.answer("Ошибка при отмене ставки")


async def process_bid_price(message: types.Message, state: FSMContext):
    try:
        price = int(message.text)
        if price <= 0:
            await message.answer("💰 Пожалуйста, введите положительное число больше нуля")
            return
    except ValueError:
        await message.answer("💰 Пожалуйста, введите корректное число (например: 500)")
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
            await message.answer("❌ Не удалось принять ставку. Возможно, аукцион завершен или заказ уже назначен.")
    except Exception as e:
        logger.error(f"Bid processing error: {e}")
        await message.answer("❌ Произошла ошибка при обработке ставки. Попробуйте еще раз позже.")

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