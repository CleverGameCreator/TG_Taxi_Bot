from core.config import Config

def format_price(price: int) -> str:
    """Форматирует цену для отображения (1 500 ₽)"""
    return f"{price:,} ₽".replace(",", " ")

def format_order(data: dict) -> str:
    """Форматирование деталей заказа для подтверждения"""
    return (
        "📝 Подтвердите детали заказа:\n\n"
        f"📍 Откуда: {data['start_point']}\n"
        f"🏁 Куда: {data['end_point']}\n"
        f"⏰ Время: {data['time']}\n"
        f"💰 Макс. цена: {format_price(data['price'])}\n\n"
        "✅ Все верно?"
    )

def format_order_for_driver(order) -> str:
    """Форматирование информации о заказе для водителей"""
    return (
        "🚖 НОВЫЙ ЗАКАЗ!\n\n"
        f"📍 Маршрут: {order.start_point} → {order.end_point}\n"
        f"⏰ Время: {order.time}\n"
        f"💰 Макс. цена: {format_price(order.price)}\n"
        f"⏳ Аукцион завершится через {Config.AUCTION_DURATION} минут"
    )

def format_driver_info(driver) -> str:
    """Форматирование информации о водителе"""
    return (
        f"👤 Водитель: {driver.full_name}\n"
        f"🚗 Автомобиль: {driver.car_model} {driver.car_number}\n"
        f"⭐ Рейтинг: {driver.rating:.1f}/5.0"
    )