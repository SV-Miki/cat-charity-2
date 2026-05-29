"""ORM-модель пожертвования."""

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import InvestmentBaseModel


class Donation(InvestmentBaseModel):
    """Модель пожертвования."""

    __tablename__ = 'donation'

    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'),
        nullable=False,
    )
    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
