import logging
from aiogram import Bot, Dispatcher, Router
from aiogram_sqlite_storage.sqlitestore import SQLStorage
from core.config import Config
from database import init_db
from utils.logger import setup_logger
from tasks.auction_expire import set_bot_instance
from bot.handlers.driver import bidding, profile, registration
from bot.handlers.client import create_order, choose_driver
from bot.handlers.common.start import router as start_router
from bot.handlers.common.feedback import router as feedback_router
from bot.handlers.common.cancel import router as cancel_router
from bot.handlers.driver.bidding import router as bidding_router
from bot.handlers.driver.profile import router as profile_router
from bot.handlers.driver.registration import router as registration_router
from bot.handlers.client.create_order import router as create_order_router
from bot.handlers.client.choose_driver import router as choose_driver_router
import asyncio

# Настройка логирования
setup_logger()
logger = logging.getLogger(__name__)

# Инициализация конфига
config = Config()

async def main():
    # Инициализация бота и диспетчера
    try:
        bot = Bot(token=config.BOT_TOKEN)
        storage = SQLStorage("database.db")
        dp = Dispatcher(storage=storage)
    except Exception as e:
        logger.exception(f"Error initializing bot: {e}")
        exit(1)

    # Установка инстанса бота для задач
    set_bot_instance(bot)

    # Инициализация БД
    init_db()

    # Включаем роутеры в диспетчер
    dp.include_router(cancel_router) # Важно: включить первым для перехвата отмены
    dp.include_router(start_router)
    dp.include_router(feedback_router)
    dp.include_router(bidding_router)
    dp.include_router(profile_router)
    dp.include_router(registration_router)
    dp.include_router(create_order_router)
    dp.include_router(choose_driver_router)

    # Запуск бота
    logger.info("Starting bot...")
    try:
        await dp.start_polling(
            bot,
            skip_updates=True,
            allowed_updates=dp.resolve_used_update_types()
        )
    except Exception as e:
        logger.exception(f"Bot stopped with error: {e}")
    finally:
        await bot.session.close()
        logger.info("Bot stopped")

if __name__ == '__main__':
    asyncio.run(main())