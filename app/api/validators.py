"""Валидаторы для API-эндпоинтов."""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models.charity_project import CharityProject

PROJECT_NAME_EXISTS_ERROR = 'Проект с таким именем уже существует!'
PROJECT_NOT_FOUND_ERROR = 'Проект не найден!'
PROJECT_CLOSED_ERROR = 'Закрытый проект нельзя редактировать!'
PROJECT_AMOUNT_ERROR = (
    'Нельзя установить значение full_amount меньше уже вложенной суммы.'
)
PROJECT_HAS_INVESTMENTS_ERROR = (
    'В проект были внесены средства, не подлежит удалению!'
)


async def check_project_exists(
    project_id: int,
    session: AsyncSession,
) -> CharityProject:
    """Проверяет, что целевой проект существует."""
    project = await charity_project_crud.get(project_id, session)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=PROJECT_NOT_FOUND_ERROR,
        )

    return project


async def check_project_name_duplicate(
    project_name: str | None,
    session: AsyncSession,
    project_id: int | None = None,
) -> None:
    """Проверяет уникальность названия целевого проекта."""
    if project_name is None:
        return

    project = await charity_project_crud.get_by_name(
        project_name,
        session,
    )

    if project is not None and project.id != project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=PROJECT_NAME_EXISTS_ERROR,
        )


def check_project_can_be_updated(project: CharityProject) -> None:
    """Проверяет, что целевой проект можно редактировать."""
    if project.fully_invested:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=PROJECT_CLOSED_ERROR,
        )


def check_project_full_amount(
    project: CharityProject,
    new_full_amount: int | None,
) -> None:
    """Проверяет новую требуемую сумму целевого проекта."""
    if new_full_amount is None:
        return

    if new_full_amount < project.invested_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=PROJECT_AMOUNT_ERROR,
        )


def check_project_can_be_deleted(project: CharityProject) -> None:
    """Проверяет, что целевой проект можно удалить."""
    if project.invested_amount > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=PROJECT_HAS_INVESTMENTS_ERROR,
        )
