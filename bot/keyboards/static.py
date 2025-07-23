from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_main_kb(user_id: int = None):
    keyboard_rows = [
        [InlineKeyboardButton(text="➕ Создать заказ", callback_data="main_create_order")]
    ]

    # Проверка типа пользователя (в реальном коде нужно запрашивать БД)
    if user_id in [123, 456, 6826384730]:  # Пример: заменить на реальную проверку
        keyboard_rows.append([InlineKeyboardButton(text="🚖 Стать водителем", callback_data="main_become_driver")])

    keyboard_rows.append([InlineKeyboardButton(text="ℹ️ Помощь", callback_data="main_help")])

    kb = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    return kb


def get_cancel_kb():
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="❌ Отмена")]], resize_keyboard=True)
    return kb


def get_confirmation_kb():
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="✅ Подтвердить")],
        [KeyboardButton(text="❌ Отмена")]
    ], resize_keyboard=True)
    return kb


def get_driver_registration_confirmation_kb() -> InlineKeyboardMarkup:
    """Inline клавиатура для подтверждения регистрации водителя"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="driver_registration_confirm")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_action")]
    ])