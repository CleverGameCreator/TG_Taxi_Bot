from sqlalchemy import create_engine, select, desc  # Добавлен create_engine
from sqlalchemy.orm import sessionmaker
from .models import User, Order, Bid, Base
from core.config import Config
from core.exceptions import OrderNotFoundError

# Создаем engine для подключения к БД
engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class BaseRepository:
    def __init__(self, session):
        self.session = session


class UserRepository(BaseRepository):
    def get_user(self, telegram_id: int) -> User:
        return self.session.scalar(
            select(User).where(User.telegram_id == telegram_id)
        )

    def create_user(self, user_data: dict) -> User:
        user = User(**user_data)
        self.session.add(user)
        self.session.commit()
        return user

    def update_user(self, telegram_id: int, update_data: dict) -> User:
        user = self.get_user(telegram_id)
        if user:
            for key, value in update_data.items():
                setattr(user, key, value)
            self.session.commit()
        return user

    def get_verified_drivers(self):
        return self.session.scalars(
            select(User).where(
                User.user_type == 'driver',
                User.verified == True
            )
        ).all()


class OrderRepository(BaseRepository):
    def create_order(self, order_data: dict) -> Order:
        order = Order(**order_data)
        self.session.add(order)
        return order

    def get_order(self, order_id: str) -> Order:
        order = self.session.scalar(
            select(Order).where(Order.id == order_id)
        )
        if not order:
            raise OrderNotFoundError(f"Order {order_id} not found")
        return order

    def update_order(self, order_id: str, update_data: dict) -> Order:
        order = self.get_order(order_id)
        for key, value in update_data.items():
            setattr(order, key, value)
        self.session.commit()
        return order

    def get_active_orders(self):
        return self.session.scalars(
            select(Order).where(Order.status == 'active')
        ).all()

    def get_orders_by_user(self, user_id: int):
        return self.session.scalars(
            select(Order).where(Order.client_id == user_id)
        ).all()


class BidRepository(BaseRepository):
    def create_bid(self, bid_data: dict) -> Bid:
        bid = Bid(**bid_data)
        self.session.add(bid)
        self.session.commit()
        return bid

    def get_bid(self, order_id: str, driver_id: int) -> Bid:
        """Получение конкретной ставки по ID заказа и водителя"""
        return self.session.scalar(
            select(Bid).where(
                Bid.order_id == order_id,
                Bid.driver_id == driver_id
            )
        )

    def get_bids_for_order(self, order_id: str) -> list[Bid]:
        """Получение всех ставок для заказа, отсортированных по цене (по убыванию)"""
        return self.session.scalars(
            select(Bid)
            .where(Bid.order_id == order_id)
            .order_by(desc(Bid.price))
        ).all()

    def get_lowest_bid(self, order_id: str) -> Bid:
        """Получение минимальной ставки для заказа"""
        return self.session.scalar(
            select(Bid)
            .where(Bid.order_id == order_id)
            .order_by(Bid.price)
            .limit(1)
        )

    def get_driver_bids(self, driver_id: int) -> list[Bid]:
        """Получение всех ставок водителя"""
        return self.session.scalars(
            select(Bid)
            .where(Bid.driver_id == driver_id)
            .order_by(desc(Bid.created_at))
        ).all()


def init_db():
    Base.metadata.create_all(bind=engine)

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()