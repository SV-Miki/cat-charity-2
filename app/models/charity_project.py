"""ORM-модель целевого проекта."""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import MAX_PROJECT_NAME_LENGTH
from app.models.base import InvestmentBaseModel


class CharityProject(InvestmentBaseModel):
    """Модель целевого благотворительного проекта."""

    __tablename__ = 'charityproject'

    name: Mapped[str] = mapped_column(
        String(MAX_PROJECT_NAME_LENGTH),
        unique=True,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
