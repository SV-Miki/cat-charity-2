"""Базовые ORM-модели приложения."""

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from app.core.db import Base


class InvestmentBaseModel(Base):
    """Абстрактная модель для объектов с инвестированием."""

    __abstract__ = True

    @declared_attr.directive
    def __table_args__(cls):
        """Добавляет ограничения на инвестиционные поля модели."""
        return (
            CheckConstraint(
                'full_amount > 0',
                name=f'ck_{cls.__tablename__}_full_amount_positive',
            ),
            CheckConstraint(
                'invested_amount >= 0',
                name=f'ck_{cls.__tablename__}_invested_amount_non_negative',
            ),
            CheckConstraint(
                'invested_amount <= full_amount',
                name=f'ck_{cls.__tablename__}_invested_not_greater_full',
            ),
        )

    id: Mapped[int] = mapped_column(primary_key=True)
    full_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    invested_amount: Mapped[int] = mapped_column(Integer, default=0)
    fully_invested: Mapped[bool] = mapped_column(Boolean, default=False)
    create_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
    )
    close_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    def __repr__(self) -> str:
        """Возвращает строковое представление объекта для отладки."""
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'full_amount={self.full_amount!r}, '
            f'invested_amount={self.invested_amount!r}, '
            f'fully_invested={self.fully_invested!r}'
            ')'
        )
