from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from bot.keyboards import static

router = Router()

@router.message(lambda message: message.text == "❌ Отмена")
async def handle_cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
        await message.answer(
            "Действие отменено.",
            reply_markup=static.get_main_kb(message.from_user.id)
        )
    else:
        await message.answer("Нет активного действия для отмены.")

@router.callback_query(lambda c: c.data == "cancel_action")
async def handle_cancel_callback(callback_query: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
        await callback_query.message.answer(
            "Действие отменено.",
            reply_markup=static.get_main_kb(callback_query.from_user.id)
        )
        await callback_query.message.edit_reply_markup(reply_markup=None)
    else:
        await callback_query.message.answer("Нет активного действия для отмены.")
    await callback_query.answer() 