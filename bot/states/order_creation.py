from aiogram.fsm.state import State, StatesGroup

class OrderCreation(StatesGroup):
    START_POINT = State()
    END_POINT = State()
    TIME = State()
    PRICE = State()
    CONFIRM = State()

class DriverRegistration(StatesGroup):
    CAR_MODEL = State()
    CAR_NUMBER = State()
    LICENSE_PHOTO = State()
    CONFIRM = State()

class DriverBidding(StatesGroup):
    PRICE = State()