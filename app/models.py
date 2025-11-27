# app/models.py
from datetime import datetime
from typing import Optional

from sqlalchemy import String, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db import Base


class PaymentDB(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    booking_id: Mapped[int] = mapped_column(index=True)
    user_id: Mapped[int] = mapped_column(index=True)

    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(10), default="VND")

    status: Mapped[str] = mapped_column(String(20), index=True)
    provider: Mapped[str] = mapped_column(String(20))
    method: Mapped[str] = mapped_column(String(20))

    paid_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    expired_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Quan hệ 1-n với events (optional, để tiện query)
    events: Mapped[list["PaymentEventDB"]] = relationship(
        back_populates="payment",
        cascade="all, delete-orphan",
    )


class PaymentEventDB(Base):
    __tablename__ = "payment_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    event_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True)

    payment_id: Mapped[int] = mapped_column(ForeignKey("payments.id"))
    payment: Mapped[PaymentDB] = relationship(back_populates="events")

    payload: Mapped[dict] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

class WebhookSubscriptionDB(Base):
    __tablename__ = "webhook_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    target_url: Mapped[str] = mapped_column(String(255))

    event_type: Mapped[str] = mapped_column(String(50), index=True)

    secret: Mapped[str] = mapped_column(String(128))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
