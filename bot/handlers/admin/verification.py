from aiogram import Router, types
from aiogram.filters import Command
from database import SessionLocal
from database.repositories import UserRepository
from bot.keyboards.inline.auction import admin_cb
from core.config import Config

router = Router()

@router.callback_query(admin_cb.filter())
async def handle_admin_action(callback: types.CallbackQuery, callback_data: admin_cb):
    """Обработчик админских действий по верификации водителей"""
    action = callback_data.action
    user_id = callback_data.user_id
    admin_id = callback.from_user.id
    
    # Проверяем, что пользователь является администратором
    if admin_id not in Config.ADMIN_IDS:
        await callback.answer("У вас нет прав для выполнения этого действия")
        return
    
    with SessionLocal() as session:
        user_repo = UserRepository(session)
        user = user_repo.get_user(user_id)
        
        if not user:
            await callback.answer("Пользователь не найден")
            return
        
        if action == "approve":
            # Подтверждаем водителя
            user_repo.update_user(user_id, {'verified': True})
            await callback.answer("Водитель подтвержден")
            
            # Уведомляем водителя
            try:
                await callback.bot.send_message(
                    user_id,
                    "✅ Поздравляем! Ваша заявка одобрена. Теперь вы можете участвовать в аукционах."
                )
            except Exception as e:
                pass  # Игнорируем ошибки отправки сообщения
                
            # Обновляем сообщение администратора
            await callback.message.edit_caption(
                caption=f"✅ Водитель @{user.username if user.username else user.full_name} подтвержден",
                reply_markup=None
            )
            
        elif action == "reject":
            # Отклоняем водителя
            user_repo.update_user(user_id, {'user_type': 'client', 'verified': False})
            await callback.answer("Заявка водителя отклонена")
            
            # Уведомляем водителя
            try:
                await callback.bot.send_message(
                    user_id,
                    "❌ К сожалению, ваша заявка отклонена. Пожалуйста, проверьте данные и попробуйте снова."
                )
            except Exception as e:
                pass  # Игнорируем ошибки отправки сообщения
                
            # Обновляем сообщение администратора
            await callback.message.edit_caption(
                caption=f"❌ Заявка водителя @{user.username if user.username else user.full_name} отклонена",
                reply_markup=None
            )

# Функция для регистрации роутера в основном приложении
def register_handlers(dp):
    dp.include_router(router)