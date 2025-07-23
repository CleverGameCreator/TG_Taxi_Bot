from celery import Celery
from core.config import Config
from database import SessionLocal
from database.repositories import OrderRepository
import asyncio
import logging

app = Celery('tasks', broker=Config.REDIS_URL)

# Глобальная переменная для бота
bot_instance = None


@app.task
def expire_auction(order_id: str):
    """Задача Celery для завершения аукциона по таймауту"""
    if not bot_instance:
        logging.error("Bot instance not set in expire_auction!")
        return

    with SessionLocal() as session:
        order_repo = OrderRepository(session)
        try:
            order = order_repo.get_order(order_id)

            if order and order.status == "active":
                # Обновляем статус заказа
                order.status = "expired"
                session.commit()

                # Импортируем здесь, чтобы избежать циклических зависимостей
                from services.notification import notify_auction_expired

                # Уведомляем участников
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(notify_auction_expired(order_id, bot_instance))
                loop.close()
        except Exception as e:
            logging.error(f"Error expiring auction for order {order_id}: {e}")


def set_bot_instance(bot):
    global bot_instance
    bot_instance = bot