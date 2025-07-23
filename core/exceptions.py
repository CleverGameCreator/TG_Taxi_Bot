class PaymentError(Exception):
    """Ошибка при обработке платежа"""

class OrderNotFoundError(Exception):
    """Заказ не найден"""

class InsufficientFundsError(Exception):
    """Недостаточно средств на балансе"""

class AuctionExpiredError(Exception):
    """Аукцион по заказу завершен"""