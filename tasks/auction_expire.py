from celery import Celery
from core.config import Config
from database import SessionLocal
from database.repositories import OrderRepository
from services.notification import notify_auction_expired
import asyncio

app = Celery('tasks', broker=Config.REDIS_URL)


@app.task
def expire_auction(order_id: str):
    """Задача Celery для завершения аукциона по таймауту"""
    with SessionLocal() as session:
        order_repo = OrderRepository(session)
        try:
            order = order_repo.get_order(order_id)

            if order.status == "active":
                order.status = "expired"
                session.commit()

                # Создаем новую event loop для асинхронных вызовов
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(notify_auction_expired(order_id, bot_instance))
                loop.close()
        except Exception as e:
            app.log.error(f"Error expiring auction for order {order_id}: {e}")


# Глобальная переменная для бота (будет установлена при запуске)
bot_instance = None


def set_bot_instance(bot):
    global bot_instance
    bot_instance = bot