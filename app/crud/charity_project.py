"""CRUD-операции для целевых проектов."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectUpdate,
)


class CRUDCharityProject(
    CRUDBase[
        CharityProject,
        CharityProjectCreate,
        CharityProjectUpdate,
    ]
):
    """CRUD-класс для целевых проектов."""

    async def get_by_name(
        self,
        project_name: str,
        session: AsyncSession,
    ) -> CharityProject | None:
        """Получает целевой проект по названию."""
        db_project = await session.execute(
            select(CharityProject).where(CharityProject.name == project_name)
        )
        return db_project.scalars().first()

    async def get_not_fully_invested(
        self,
        session: AsyncSession,
    ) -> list[CharityProject]:
        """Получает открытые целевые проекты."""
        db_projects = await session.execute(
            select(CharityProject)
            .where(CharityProject.fully_invested.is_(False))
            .order_by(CharityProject.create_date)
        )
        return list(db_projects.scalars().all())


charity_project_crud = CRUDCharityProject(CharityProject)
