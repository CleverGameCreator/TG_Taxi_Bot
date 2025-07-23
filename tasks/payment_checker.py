from celery import Celery
from core.config import Config
from database import SessionLocal
from database.repositories import OrderRepository
import requests

app = Celery('tasks', broker=Config.REDIS_URL)


@app.task
def check_payment_status(payment_id: str):
    """Проверка статуса платежа"""
    # В реальном приложении здесь будет запрос к платежному шлюзу
    with SessionLocal() as session:
        order_repo = OrderRepository(session)
        orders = order_repo.get_orders_by_payment_id(payment_id)

        for order in orders:
            # Предположим, что платеж успешен
            order.payment_status = 'completed'
            session.commit()