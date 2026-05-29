"""API-эндпоинты для пожертвований."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.crud.charity_project import charity_project_crud
from app.models.user import User
from app.models.donation import Donation
from app.schemas.donation import (
    DonationCreate,
    DonationDB,
    DonationFullInfoDB,
)
from app.services.investment import invest_objects


router = APIRouter()


@router.get(
    '/',
    response_model=list[DonationFullInfoDB],
    summary='Получить все пожертвования',
    description=(
            'Показать список всех пожертвований.\n\n'
            'Только для суперюзеров.'
    ),
)
async def get_all_donations(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    _: Annotated[User, Depends(current_superuser)],
):
    """Возвращает список всех пожертвований."""
    return await donation_crud.get_multi(session)


@router.get(
    '/my',
    response_model=list[DonationDB],
    summary='Получить мои пожертвования',
    description=(
        'Показать список пожертвований пользователя, выполняющего запрос.\n\n'
        'Только для зарегистрированных пользователей.'
    ),
)
async def get_user_donations(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[User, Depends(current_user)],
):
    """Возвращает список пожертвований текущего пользователя."""
    return await donation_crud.get_by_user(user.id, session)


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude_none=True,
    summary='Создать пожертвование',
    description=(
            'Сделать пожертвование.\n\n'
            'Только для зарегистрированных пользователей.'
    ),
)
async def create_donation(
    donation: DonationCreate,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[User, Depends(current_user)],
):
    """Создаёт новое пожертвование."""
    donation_data = donation.model_dump()
    new_donation = Donation(
        **donation_data,
        user_id=user.id,
    )
    session.add(new_donation)
    await session.flush()

    projects = await charity_project_crud.get_not_fully_invested(session)

    await invest_objects(
        sources=[new_donation],
        targets=projects,
        session=session,
    )

    return new_donation
