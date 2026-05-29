"""Базовый CRUD-класс."""

from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import Base


ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Базовый класс для CRUD-операций."""

    def __init__(self, model: type[ModelType]):
        """Инициализирует CRUD-класс моделью."""
        self.model = model

    async def get(
        self,
        object_id: int,
        session: AsyncSession,
    ) -> ModelType | None:
        """Получает объект по id."""
        db_object = await session.execute(
            select(self.model).where(self.model.id == object_id)
        )
        return db_object.scalars().first()

    async def get_multi(
        self,
        session: AsyncSession,
    ) -> list[ModelType]:
        """Получает список объектов."""
        db_objects = await session.execute(select(self.model))
        return db_objects.scalars().all()

    async def create(
        self,
        object_in: CreateSchemaType,
        session: AsyncSession,
        commit: bool = True,
    ) -> ModelType:
        """Создаёт объект."""
        object_data = object_in.model_dump()
        db_object = self.model(**object_data)
        session.add(db_object)
        await session.flush()

        if commit:
            await session.commit()
            await session.refresh(db_object)

        return db_object

    async def update(
        self,
        db_object: ModelType,
        object_in: UpdateSchemaType,
        session: AsyncSession,
    ) -> ModelType:
        """Обновляет объект."""
        object_data = object_in.model_dump(exclude_unset=True)

        for field, value in object_data.items():
            setattr(db_object, field, value)

        session.add(db_object)
        await session.commit()
        await session.refresh(db_object)
        return db_object

    async def remove(
        self,
        db_object: ModelType,
        session: AsyncSession,
    ) -> ModelType:
        """Удаляет объект."""
        await session.delete(db_object)
        await session.commit()
        return db_object
