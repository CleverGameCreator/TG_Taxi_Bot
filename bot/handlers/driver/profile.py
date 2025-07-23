from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from bot.states import DriverRegistration
from database import SessionLocal
from database.repositories import UserRepository
from bot.keyboards import static
from core.config import Config

# Создаем роутер для этого модуля
router = Router()


async def start_registration(message: types.Message):
    await message.bot.send_message(
        message.from_user.id,
        "🚗 Введите марку и модель вашего автомобиля:",
        reply_markup=static.get_cancel_kb()
    )
    await message.delete()  # Удаляем исходное сообщение
    await DriverRegistration.CAR_MODEL.set()


async def process_car_model(message: types.Message, state: FSMContext):
    await state.update_data(car_model=message.text)
    await message.answer("🔢 Введите номер вашего автомобиля:")
    await DriverRegistration.CAR_NUMBER.set()


async def process_car_number(message: types.Message, state: FSMContext):
    await state.update_data(car_number=message.text)
    await message.answer("📸 Отправьте фото вашего водительского удостоверения:")
    await DriverRegistration.LICENSE_PHOTO.set()


async def process_license_photo(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("Пожалуйста, отправьте фото документа")
        return

    # Сохраняем file_id последнего фото (наивысшего качества)
    await state.update_data(license_photo=message.photo[-1].file_id)
    await message.answer(
        "✅ Регистрационные данные получены!\n"
        "Отправьте их на проверку администратору?",
        reply_markup=static.get_confirmation_kb()
    )
    await DriverRegistration.CONFIRM.set()


async def confirm_registration(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    with SessionLocal() as session:
        user_repo = UserRepository(session)
        user = user_repo.update_user(callback.from_user.id, {
            'car_model': data.get('car_model', ''),
            'car_number': data.get('car_number', ''),
            'license_photo': data.get('license_photo', ''),
            'user_type': 'driver'
        })

    await state.clear()
    await callback.message.answer(
        "✅ Ваши данные отправлены на проверку!\n"
        "Ожидайте подтверждения администратора.",
        reply_markup=static.get_main_kb(callback.from_user.id)
    )

    # Уведомление администраторов
    for admin_id in Config.ADMIN_IDS:
        try:
            await callback.bot.send_message(
                admin_id,
                f"⚠️ Новая заявка водителя!\n"
                f"👤 Пользователь: @{user.username if user.username else 'нет'} ({user.full_name})\n"
                f"🚗 Автомобиль: {user.car_model} {user.car_number}"
            )
        except Exception as e:
            # Логирование ошибки отправки уведомления
            pass


def register_handlers(router_instance: Router):
    router_instance.message.register(start_registration, lambda message: message.text == "🚖 Стать водителем", lambda message: message.state == None)
    router_instance.message.register(process_car_model, DriverRegistration.CAR_MODEL)
    router_instance.message.register(process_car_number, DriverRegistration.CAR_NUMBER)
    router_instance.message.register(process_license_photo, DriverRegistration.LICENSE_PHOTO)
    router_instance.callback_query.register(confirm_registration, lambda callback_query: callback_query.data == "confirm", DriverRegistration.CONFIRM)