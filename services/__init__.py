# Убираем импорт, который может вызывать циклическую зависимость
from .payment import process_payment, add_funds, process_order_payment
from .notification import notify_drivers_about_order, notify_auction_expired, notify_order_accepted
from .rating import update_rating

# Ленивый импорт для избежания циклических зависимостей
try:
    from .auction import start_auction, process_bid, complete_auction
except ImportError:
    import sys
    import services.auction as auction_module
    sys.modules['services.auction'] = auction_module
    start_auction = auction_module.start_auction
    process_bid = auction_module.process_bid
    complete_auction = auction_module.complete_auction

__all__ = [
    'process_payment', 'add_funds', 'process_order_payment',
    'notify_drivers_about_order', 'notify_auction_expired', 'notify_order_accepted',
    'update_rating',
    'start_auction', 'process_bid', 'complete_auction'
]