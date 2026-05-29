"""CRUD-операции для пожертвований."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.donation import Donation
from app.schemas.donation import DonationCreate


class CRUDDonation(CRUDBase[Donation, DonationCreate, DonationCreate]):
    """CRUD-класс для пожертвований."""

    async def get_not_fully_invested(
        self,
        session: AsyncSession,
    ) -> list[Donation]:
        """Получает не полностью распределённые пожертвования."""
        db_donations = await session.execute(
            select(Donation)
            .where(Donation.fully_invested.is_(False))
            .order_by(Donation.create_date)
        )
        return db_donations.scalars().all()

    async def get_by_user(
        self,
        user_id: int,
        session: AsyncSession,
    ) -> list[Donation]:
        """Получает пожертвования пользователя."""
        db_donations = await session.execute(
            select(Donation)
            .where(Donation.user_id == user_id)
            .order_by(Donation.create_date)
        )
        return db_donations.scalars().all()


donation_crud = CRUDDonation(Donation)
