import uvicorn
import secrets
from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import engine, Base, get_session
from app.models import PaymentDB, PaymentEventDB, WebhookSubscriptionDB
from app.schemas import (
    PaymentCreate,
    PaymentRead,
    PaymentStatusUpdate,
    WebhookSubscriptionCreate,
    WebhookSubscriptionRead,
)
from app.repositories import (
    list_payments_repo,
    get_payment_by_id_repo,
    list_webhook_subscriptions_repo,
)
from app.events import map_status_to_event_type, build_payment_event_payload


app = FastAPI()


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.post("/payments", response_model=PaymentRead, status_code=201)
async def create_payment(
    payload: PaymentCreate,
    db: AsyncSession = Depends(get_session),
):
    payment = PaymentDB(
        booking_id=payload.booking_id,
        user_id=payload.user_id,
        amount=payload.amount,
        currency=payload.currency,
        provider=payload.provider,
        method=payload.method,
        status="PENDING",   # default khi mới tạo
    )
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment

@app.get("/payments", response_model=List[PaymentRead])
async def list_payments(
    booking_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    provider: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_session),
):
    payments = await list_payments_repo(
        db=db,
        booking_id=booking_id,
        status=status,
        provider=provider,
        limit=limit,
        offset=offset,
    )
    return payments

@app.put(
    "/payments/{payment_id}/status",
    response_model=PaymentRead,
    summary="Cập nhật trạng thái thanh toán và tạo event",
)
async def update_payment_status(
    payment_id: int,
    status_update: PaymentStatusUpdate,
    db: AsyncSession = Depends(get_session),
):
    payment = await get_payment_by_id_repo(db, payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    new_status = status_update.new_status.upper()
    payment.status = new_status

    now = datetime.utcnow()
    if new_status == "SUCCEEDED":
        payment.paid_at = now
    elif new_status == "EXPIRED":
        payment.expired_at = now

    await db.flush()

    event_type = map_status_to_event_type(new_status)
    event_payload = build_payment_event_payload(payment, event_type)

    new_event = PaymentEventDB(
        event_id=event_payload["event_id"],
        event_type=event_type,
        payment_id=payment.id,
        payload=event_payload,
    )
    db.add(new_event)

    await db.commit()
    await db.refresh(payment)

    return payment

@app.post(
    "/webhook-subscriptions",
    response_model=WebhookSubscriptionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký nhận webhook cho một event",
)
async def create_webhook_subscription(
    payload: WebhookSubscriptionCreate,
    db: AsyncSession = Depends(get_session),
):
    secret = payload.secret or secrets.token_hex(32)

    db_obj = WebhookSubscriptionDB(
        target_url=payload.target_url,
        event_type=payload.event_type,
        is_active=payload.is_active,
        secret=secret,
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


@app.get(
    "/webhook-subscriptions",
    response_model=list[WebhookSubscriptionRead],
    summary="Danh sách webhook subscriptions (filter + pagination)",
)
async def list_webhook_subscriptions(
    event_type: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_session),
):
    subs = await list_webhook_subscriptions_repo(
        db=db,
        event_type=event_type,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )
    return subs




if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
