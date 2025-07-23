
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from bot.states import DriverRegistration
from database import SessionLocal
from database.repositories import UserRepository
from bot.keyboards import static
from core.config import Config
from aiogram.types import CallbackQuery

router = Router()


async def start_registration(message: types.Message, state: FSMContext):
    await state.set_state(DriverRegistration.CAR_MODEL)
    await message.answer(
        "🚗 Введите марку и модель вашего автомобиля:",
        reply_markup=static.get_cancel_kb()
    )


async def process_car_model(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data = data or {}
    data['car_model'] = message.text
    await state.set_data(data)
    await message.answer("🔢 Введите номер вашего автомобиля:")
    await state.set_state(DriverRegistration.CAR_NUMBER)


async def process_car_number(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data = data or {}
    data['car_number'] = message.text
    await state.set_data(data)
    await message.answer("📸 Отправьте фото вашего водительского удостоверения:")
    await state.set_state(DriverRegistration.LICENSE_PHOTO)


async def process_license_photo(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("Пожалуйста, отправьте фото документа")
        return

    data = await state.get_data()
    data = data or {}
    data['license_photo'] = message.photo[-1].file_id
    await state.set_data(data)
    await message.answer(
        "✅ Регистрационные данные получены!\n"
        "Отправьте их на проверку администратору?",
        reply_markup=static.get_driver_registration_confirmation_kb()
    )
    await state.set_state(DriverRegistration.CONFIRM)


@router.callback_query(lambda c: c.data == "driver_registration_confirm", DriverRegistration.CONFIRM)
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
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "✅ Ваши данные отправлены на проверку!\n"
        "Ожидайте подтверждения администратора.",
        reply_markup=static.get_main_kb(callback.from_user.id)
    )

    for admin_id in Config.ADMIN_IDS:
        try:
            await callback.bot.send_message(
                admin_id,
                f"⚠️ Новая заявка водителя!\n"
                f"👤 Пользователь: @{user.username if user.username else 'нет'} ({user.full_name})\n"
                f"🚗 Автомобиль: {user.car_model} {user.car_number}"
            )
        except Exception as e:
            pass
    await callback.answer("Данные отправлены на проверку!")


# Регистрация обработчиков
router.message.register(process_car_model, DriverRegistration.CAR_MODEL)
router.message.register(process_car_number, DriverRegistration.CAR_NUMBER)
router.message.register(process_license_photo, DriverRegistration.LICENSE_PHOTO)
router.callback_query.register(confirm_registration, lambda c: c.data == "driver_registration_confirm", DriverRegistration.CONFIRM) 