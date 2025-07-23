from aiogram import Router, types
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(lambda message: message.text and "отзыв" in message.text.lower())
async def handle_feedback(message: types.Message, state: FSMContext):
    await message.answer("Спасибо за ваш отзыв!")
    await state.clear()


@router.message(lambda message: message.text and "ℹ️ помощь" in message.text.lower())
async def handle_help_button(message: types.Message):
    await message.answer("Чем могу помочь?")

def register_handlers(router_instance: Router):
    router_instance.include_router(router)