"""Pydantic-схемы для пользователей."""

from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    """Схема пользователя в ответе API."""


class UserCreate(schemas.BaseUserCreate):
    """Схема создания пользователя."""


class UserUpdate(schemas.BaseUserUpdate):
    """Схема обновления пользователя."""
