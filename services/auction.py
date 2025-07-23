from datetime import datetime
from sqlalchemy import select
from database import SessionLocal
from database.models import Bid
from core.exceptions import AuctionExpiredError
from celery import current_app


def start_auction(order_id: str):
    """Запуск аукциона для заказа"""
    with SessionLocal() as session:
        from database.repositories import OrderRepository

        order_repo = OrderRepository(session)
        try:
            order = order_repo.get_order(order_id)

            if order:
                # Используем Celery через current_app
                current_app.send_task(
                    'tasks.auction_expire.expire_auction',
                    args=[order_id],
                    eta=order.expires_at
                )
        except Exception as e:
            logging.error(f"Error starting auction: {e}")


def process_bid(driver_id: int, order_id: str, price: int) -> bool:
    """Обработка новой ставки"""
    with SessionLocal() as session:
        from database.repositories import OrderRepository, BidRepository

        order_repo = OrderRepository(session)
        bid_repo = BidRepository(session)

        try:
            order = order_repo.get_order(order_id)
            if not order:
                return False

            # Проверяем активен ли аукцион
            if order.status != 'active' or datetime.utcnow() > order.expires_at:
                raise AuctionExpiredError("Аукцион по этому заказу завершен")

            # Проверяем не сделал ли уже ставку этот водитель
            stmt = select(Bid).where(
                Bid.order_id == order_id,
                Bid.driver_id == driver_id
            )
            existing_bid = session.scalar(stmt)

            if existing_bid:
                # Обновляем существующую ставку
                existing_bid.price = price
            else:
                # Создаем новую ставку
                bid = Bid(
                    order_id=order_id,
                    driver_id=driver_id,
                    price=price
                )
                session.add(bid)

            session.commit()
            return True

        except Exception as e:
            session.rollback()
            raise e


def complete_auction(order_id: str, driver_id: int):
    """Завершение аукциона выбором водителя"""
    with SessionLocal() as session:
        from database.repositories import OrderRepository

        order_repo = OrderRepository(session)

        try:
            order = order_repo.get_order(order_id)
            if not order:
                raise ValueError("Заказ не найден")

            # Находим ставку выбранного водителя
            stmt = select(Bid).where(
                Bid.order_id == order_id,
                Bid.driver_id == driver_id
            )
            bid = session.scalar(stmt)

            if not bid:
                raise ValueError("Водитель не делал ставку на этот заказ")

            # Обновляем заказ
            order.driver_id = driver_id
            order.price = bid.price
            order.status = 'assigned'
            session.commit()

            return order

        except Exception as e:
            session.rollback()
            raise e