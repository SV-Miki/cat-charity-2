"""Pydantic-схемы для целевых проектов."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, PositiveInt

from app.core.constants import (
    MAX_PROJECT_NAME_LENGTH,
    MIN_PROJECT_DESCRIPTION_LENGTH,
    MIN_PROJECT_NAME_LENGTH,
)


class CharityProjectBase(BaseModel):
    """Базовая схема целевого проекта."""

    name: str | None = Field(
        default=None,
        min_length=MIN_PROJECT_NAME_LENGTH,
        max_length=MAX_PROJECT_NAME_LENGTH,
    )
    description: str | None = Field(
        default=None,
        min_length=MIN_PROJECT_DESCRIPTION_LENGTH,
    )
    full_amount: PositiveInt | None = None

    model_config = ConfigDict(extra='forbid')


class CharityProjectCreate(CharityProjectBase):
    """Схема создания целевого проекта."""

    name: str = Field(
        min_length=MIN_PROJECT_NAME_LENGTH,
        max_length=MAX_PROJECT_NAME_LENGTH,
    )
    description: str = Field(
        min_length=MIN_PROJECT_DESCRIPTION_LENGTH,
    )
    full_amount: PositiveInt


class CharityProjectUpdate(CharityProjectBase):
    """Схема обновления целевого проекта."""


class CharityProjectDB(CharityProjectCreate):
    """Схема целевого проекта в ответе API."""

    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
