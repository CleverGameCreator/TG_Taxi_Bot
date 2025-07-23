from database import SessionLocal
from database.repositories import UserRepository


def update_rating(user_id: int, new_rating: int):
    """Обновление рейтинга пользователя"""
    with SessionLocal() as session:
        user_repo = UserRepository(session)
        user = user_repo.get_user(user_id)

        if user:
            # Рассчет нового рейтинга (простое скользящее среднее)
            total_ratings = user.rating * user.rating_count
            user.rating = (total_ratings + new_rating) / (user.rating_count + 1)
            user.rating_count += 1
            session.commit()

        return user.rating if user else None