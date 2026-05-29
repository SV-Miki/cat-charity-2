"""Функции для начального наполнения базы данных."""

from pwdlib import PasswordHash
from sqlalchemy import select

from app.core.db import AsyncSessionLocal
from app.models.user import User


async def create_user(
    email: str,
    password: str,
    is_superuser: bool = False,
) -> User:
    """Создаёт пользователя, если он ещё не существует."""
    password_hash = PasswordHash.recommended()
    hashed_password = password_hash.hash(password)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalars().first()

        if user is not None:
            user.hashed_password = hashed_password
            user.is_active = True
            user.is_superuser = is_superuser
            user.is_verified = False
        else:
            user = User(
                email=email,
                hashed_password=hashed_password,
                is_active=True,
                is_superuser=is_superuser,
                is_verified=False,
            )
            session.add(user)

        await session.commit()
        await session.refresh(user)
        return user
