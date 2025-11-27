from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import WebhookSubscriptionDB
from app.models import PaymentDB


async def list_payments_repo(
    db: AsyncSession,
    booking_id: int | None = None,
    status: str | None = None,
    provider: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[PaymentDB]:
    stmt = select(PaymentDB).order_by(PaymentDB.created_at.desc())

    conditions = []

    if booking_id is not None:
        conditions.append(PaymentDB.booking_id == booking_id)

    if status is not None:
        conditions.append(PaymentDB.status == status)

    if provider is not None:
        conditions.append(PaymentDB.provider == provider)

    if conditions:
        stmt = stmt.where(*conditions)

    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)
    return result.scalars().all()

async def get_payment_by_id_repo(
    db: AsyncSession, payment_id: int
) -> PaymentDB | None:
    stmt = select(PaymentDB).where(PaymentDB.id == payment_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def list_webhook_subscriptions_repo(
    db: AsyncSession,
    event_type: str | None = None,
    is_active: bool | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[WebhookSubscriptionDB]:
    stmt = select(WebhookSubscriptionDB).order_by(
        WebhookSubscriptionDB.created_at.desc()
    )

    conditions: list = []

    if event_type is not None:
        conditions.append(WebhookSubscriptionDB.event_type == event_type)

    if is_active is not None:
        conditions.append(WebhookSubscriptionDB.is_active == is_active)

    if conditions:
        stmt = stmt.where(*conditions)

    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)
    return result.scalars().all()
