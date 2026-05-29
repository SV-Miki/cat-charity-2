"""Настройка пользователей и аутентификации."""

from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users import (
    BaseUserManager,
    FastAPIUsers,
    IntegerIDMixin,
    InvalidPasswordException,
)
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_async_session
from app.models.user import User


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """Менеджер пользователей."""

    reset_password_token_secret = settings.secret
    verification_token_secret = settings.secret

    async def validate_password(
        self,
        password: str,
        user: User,
    ) -> None:
        """Проверяет пароль пользователя."""
        if len(password) < 3:
            raise InvalidPasswordException(
                reason='Password should be at least 3 characters'
            )


async def get_user_db(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    """Генерирует объект для работы с пользователями в БД."""
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    """Генерирует менеджер пользователей."""
    yield UserManager(user_db)


def get_jwt_strategy() -> JWTStrategy:
    """Возвращает JWT-стратегию."""
    return JWTStrategy(
        secret=settings.secret,
        lifetime_seconds=3600,
    )


bearer_transport = BearerTransport(tokenUrl='auth/jwt/login')

auth_backend = AuthenticationBackend(
    name='jwt',
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(
    active=True,
    superuser=True,
)
