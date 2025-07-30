import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")
    COMMISSION_RATE = float(os.getenv("COMMISSION_RATE", 0.1))
    AUCTION_DURATION = int(os.getenv("AUCTION_DURATION", 15))
    TIMEZONE = os.getenv("TIMEZONE", "Europe/Moscow")
    THROTTLE_LIMIT = float(os.getenv("THROTTLE_LIMIT", 0.5))
    ADMIN_IDS = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]

    @staticmethod
    def format_price(price: float) -> str:
        """Форматирует цену с рублями и копейками"""
        rubles = int(price)
        kopecks = int((price - rubles) * 100)
        if kopecks > 0:
            return f"{rubles:,} ₽ {kopecks:02d} коп.".replace(",", " ")
        else:
            return f"{rubles:,} ₽".replace(",", " ")