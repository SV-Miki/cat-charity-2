"""Сервис распределения пожертвований по целевым проектам."""

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import InvestmentBaseModel


def close_investment_object(
    investment_object: InvestmentBaseModel,
) -> InvestmentBaseModel:
    """Закрывает полностью инвестированный объект."""
    investment_object.fully_invested = True
    investment_object.close_date = datetime.now()
    return investment_object


def get_available_amount(
    investment_object: InvestmentBaseModel,
) -> int:
    """Возвращает свободную для инвестирования сумму."""
    return investment_object.full_amount - investment_object.invested_amount


def invest_amount(
    source: InvestmentBaseModel,
    target: InvestmentBaseModel,
) -> None:
    """Переносит доступную сумму из источника в цель."""
    available_source_amount = get_available_amount(source)
    required_target_amount = get_available_amount(target)
    investment_amount = min(
        available_source_amount,
        required_target_amount,
    )

    source.invested_amount += investment_amount
    target.invested_amount += investment_amount

    if source.invested_amount == source.full_amount:
        close_investment_object(source)

    if target.invested_amount == target.full_amount:
        close_investment_object(target)


async def invest_objects(
    sources: list[InvestmentBaseModel],
    targets: list[InvestmentBaseModel],
    session: AsyncSession,
) -> None:
    """Распределяет средства из источников по целевым объектам."""
    for source in sources:
        for target in targets:
            if source.fully_invested:
                break

            if target.fully_invested:
                continue

            invest_amount(source, target)
            session.add(source)
            session.add(target)

    for source in sources:
        session.add(source)

    for target in targets:
        session.add(target)

    await session.commit()

    for source in sources:
        await session.refresh(source)

    for target in targets:
        await session.refresh(target)
