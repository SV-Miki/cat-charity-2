"""API-эндпоинты для целевых проектов."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_project_can_be_deleted,
    check_project_can_be_updated,
    check_project_exists,
    check_project_full_amount,
    check_project_name_duplicate,
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models.user import User
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectDB,
    CharityProjectUpdate,
)
from app.services.investment import close_investment_object, invest_objects

router = APIRouter()


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    summary='Получить все целевые проекты',
    description='Показать список всех целевых проектов.',
)
async def get_all_charity_projects(
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Возвращает список всех целевых проектов."""
    return await charity_project_crud.get_multi(session)


@router.post(
    '/',
    response_model=CharityProjectDB,
    summary='Создать целевой проект',
    description='Создать целевой проект.',
)
async def create_charity_project(
    project: CharityProjectCreate,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    _: Annotated[User, Depends(current_superuser)],
):
    """Создаёт новый целевой проект."""
    await check_project_name_duplicate(project.name, session)

    new_project = await charity_project_crud.create(
        project,
        session,
        commit=False,
    )
    donations = await donation_crud.get_not_fully_invested(session)

    await invest_objects(
        sources=donations,
        targets=[new_project],
        session=session,
    )

    return new_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    summary='Обновить целевой проект',
    description=(
        'Редактировать целевой проект.\n\n'
        'Закрытый проект нельзя редактировать;\n'
        'нельзя установить требуемую сумму меньше уже вложенной.'
    ),
)
async def update_charity_project(
    project_id: int,
    project_in: CharityProjectUpdate,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    _: Annotated[User, Depends(current_superuser)],
):
    """Обновляет целевой проект."""
    project = await check_project_exists(project_id, session)
    check_project_can_be_updated(project)
    check_project_full_amount(project, project_in.full_amount)
    await check_project_name_duplicate(
        project_in.name,
        session,
        project_id=project_id,
    )

    updated_project = await charity_project_crud.update(
        project,
        project_in,
        session,
    )

    if updated_project.full_amount == updated_project.invested_amount:
        close_investment_object(updated_project)
        session.add(updated_project)
        await session.commit()
        await session.refresh(updated_project)

    return updated_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    summary='Удалить целевой проект',
    description=(
        'Удалить целевой проект.\n\n'
        'Нельзя удалить проект, в который уже были инвестированы средства.'
    ),
)
async def delete_charity_project(
    project_id: int,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    _: Annotated[User, Depends(current_superuser)],
):
    """Удаляет целевой проект."""
    project = await check_project_exists(project_id, session)
    check_project_can_be_deleted(project)

    return await charity_project_crud.remove(project, session)
