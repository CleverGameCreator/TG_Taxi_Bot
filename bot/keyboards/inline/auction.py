from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from core.config import Config
from pydantic import Field # Добавляем импорт Field

# Определение callback data для заказов
class OrderCallbackData(CallbackData, prefix='order'): # Добавлен префикс
    action: str = Field()
    order_id: str = Field()

order_cb = OrderCallbackData

# Определение callback data для ставок
class BidCallbackData(CallbackData, prefix='bid'): # Добавлен префикс
    action: str = Field()
    order_id: str = Field()

bid_cb = BidCallbackData

# Определение callback data для водителей
class DriverCallbackData(CallbackData, prefix='driver'): # Добавлен префикс
    action: str = Field()
    driver_id: str = Field()
    order_id: str = Field()

driver_cb = DriverCallbackData

# Определение callback data для админских действий
class AdminCallbackData(CallbackData, prefix='admin'):
    action: str = Field()
    user_id: int = Field()
    
admin_cb = AdminCallbackData


def get_bid_kb(order_id: str) -> InlineKeyboardMarkup:
    """Клавиатура для участия в аукционе"""
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(
            "💵 Предложить цену",
            callback_data=bid_cb.new(action="create", order_id=order_id)
        ),
        InlineKeyboardButton(
            "🔄 Обновить",
            callback_data=bid_cb.new(action="refresh", order_id=order_id)
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            "❌ Отменить ставку",
            callback_data=bid_cb.new(action="cancel", order_id=order_id)
        )
    )
    return keyboard


def get_driver_choice_kb(order_id: str, bids: list) -> InlineKeyboardMarkup:
    """Клавиатура для выбора водителя из предложенных ставок"""
    kb = InlineKeyboardMarkup(row_width=1)

    for bid in bids:
        # Используем метод format_price из Config
        formatted_price = Config.format_price(bid.price)
        kb.add(InlineKeyboardButton(
            f"🚗 {bid.driver.full_name} - {formatted_price}",
            callback_data=driver_cb.new(
                action="select",
                driver_id=bid.driver.telegram_id,
                order_id=order_id
            )
        ))

    kb.add(InlineKeyboardButton(
        "❌ Отменить заказ",
        callback_data=order_cb.new(action="cancel", order_id=order_id)
    ))

    return kb


def get_order_confirmation_kb() -> InlineKeyboardMarkup:
    """Клавиатура для подтверждения заказа"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="order_confirm")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_action")]
    ])