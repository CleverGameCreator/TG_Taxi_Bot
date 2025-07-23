from aiogram import Bot
from database import SessionLocal
from database.repositories import OrderRepository, UserRepository
from utils.formatters import format_order_for_driver
from core.config import Config
import logging
from bot.keyboards.inline import auction

logger = logging.getLogger(__name__)


async def notify_drivers_about_order(order_id: str, bot: Bot):
    """Уведомление водителей о новом заказе"""
    with SessionLocal() as session:
        user_repo = UserRepository(session)
        order_repo = OrderRepository(session)

        try:
            order = order_repo.get_order(order_id)
            if not order:
                logger.error(f"Order {order_id} not found for notification")
                return

            drivers = user_repo.get_verified_drivers()

            for driver in drivers:
                try:
                    await bot.send_message(
                        driver.telegram_id,
                        format_order_for_driver(order),
                        reply_markup=auction.get_bid_kb(order_id)
                    )
                except Exception as e:
                    logger.error(f"Error notifying driver {driver.telegram_id}: {e}")
        except Exception as e:
            logger.error(f"Error in notify_drivers_about_order: {e}")


async def notify_auction_expired(order_id: str, bot: Bot):
    """Уведомление об истечении аукциона (с явным параметром bot)"""
    with SessionLocal() as session:
        order_repo = OrderRepository(session)
        user_repo = UserRepository(session)

        try:
            order = order_repo.get_order(order_id)
            if not order:
                logger.warning(f"Order {order_id} not found for expiration notification")
                return

            # Уведомление клиента
            try:
                await bot.send_message(
                    order.client.telegram_id,
                    f"⏳ Аукцион по заказу #{order_id} завершен без выбора водителя"
                )
            except Exception as e:
                logger.error(f"Error notifying client: {e}")

            # Уведомление водителей, участвовавших в аукционе
            driver_ids = {bid.driver_id for bid in order.bids}
            for driver_id in driver_ids:
                try:
                    await bot.send_message(
                        driver_id,
                        f"⏳ Аукцион по заказу #{order_id} завершен, водитель не выбран"
                    )
                except Exception as e:
                    logger.error(f"Error notifying driver {driver_id}: {e}")
        except Exception as e:
            logger.error(f"Error in notify_auction_expired: {e}")


async def notify_order_accepted(order_id: str, bot: Bot):
    """Уведомление о принятии заказа"""
    with SessionLocal() as session:
        order_repo = OrderRepository(session)

        try:
            order = order_repo.get_order(order_id)
            if not order:
                logger.warning(f"Order {order_id} not found for acceptance notification")
                return

            # Уведомление клиента
            try:
                await bot.send_message(
                    order.client.telegram_id,
                    f"✅ Ваш заказ #{order_id} принят водителем!\n"
                    f"🚗 Водитель: {order.driver.full_name}\n"
                    f"📞 Контакт: @{order.driver.username if order.driver.username else 'нет'}"
                )
            except Exception as e:
                logger.error(f"Error notifying client: {e}")

            # Уведомление водителя
            try:
                await bot.send_message(
                    order.driver.telegram_id,
                    f"✅ Вы приняли заказ #{order_id}!\n"
                    f"👤 Клиент: {order.client.full_name}\n"
                    f"📞 Контакт: @{order.client.username if order.client.username else 'нет'}\n"
                    f"📍 Маршрут: {order.start_point} → {order.end_point}"
                )
            except Exception as e:
                logger.error(f"Error notifying driver: {e}")
        except Exception as e:
            logger.error(f"Error in notify_order_accepted: {e}")