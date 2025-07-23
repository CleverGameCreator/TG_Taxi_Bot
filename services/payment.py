from database import SessionLocal
from database.repositories import UserRepository, OrderRepository
from core.exceptions import InsufficientFundsError
from core.config import Config  # Добавлен импорт Config


def process_payment(client_id: int, amount: float):
    """Обработка платежа клиента"""
    with SessionLocal() as session:
        user_repo = UserRepository(session)
        user = user_repo.get_user(client_id)

        if user.balance < amount:
            raise InsufficientFundsError("Недостаточно средств на балансе")

        user.balance -= amount
        session.commit()
        return True


def add_funds(user_id: int, amount: float):
    """Пополнение баланса"""
    with SessionLocal() as session:
        user_repo = UserRepository(session)
        user = user_repo.get_user(user_id)

        user.balance += amount
        session.commit()
        return user.balance


def process_order_payment(order_id: str):
    """Обработка оплаты заказа"""
    with SessionLocal() as session:
        order_repo = OrderRepository(session)
        order = order_repo.get_order(order_id)

        if not order:
            return False

        # Рассчитываем окончательную цену с комиссией
        commission = order.price * Config.COMMISSION_RATE
        driver_amount = order.price - commission

        # Списание средств с клиента
        if not process_payment(order.client_id, order.price):
            return False

        # Зачисление средств водителю
        add_funds(order.driver_id, driver_amount)

        # Обновление статуса заказа
        order.status = 'paid'
        session.commit()

        return True