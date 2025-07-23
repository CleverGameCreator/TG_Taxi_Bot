from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
from core.config import Config

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    username = Column(String(50), nullable=True)
    user_type = Column(String(10), nullable=False)  # client/driver
    rating = Column(Float, default=5.0)
    rating_count = Column(Integer, default=0)
    balance = Column(Float, default=0.0)
    car_model = Column(String(50), nullable=True)
    car_number = Column(String(20), nullable=True)
    license_photo = Column(String, nullable=True)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="client", foreign_keys="Order.client_id")
    bids = relationship("Bid", back_populates="driver")


class Order(Base):
    __tablename__ = 'orders'

    id = Column(String(36), primary_key=True)
    client_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    driver_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    start_point = Column(String(200), nullable=False)
    end_point = Column(String(200), nullable=False)
    distance = Column(Float, nullable=True)
    time = Column(String(5), nullable=False)  # HH:MM
    price = Column(Integer, nullable=False)
    status = Column(String(20), default="active")  # active/completed/expired/canceled
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

    client = relationship("User", foreign_keys=[client_id], back_populates="orders")
    driver = relationship("User", foreign_keys=[driver_id])
    bids = relationship("Bid", back_populates="order")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expires_at = datetime.utcnow() + timedelta(minutes=Config.AUCTION_DURATION)


class Bid(Base):
    __tablename__ = 'bids'

    id = Column(String(36), primary_key=True)
    order_id = Column(String(36), ForeignKey('orders.id'), nullable=False)
    driver_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    price = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="bids")
    driver = relationship("User", back_populates="bids")