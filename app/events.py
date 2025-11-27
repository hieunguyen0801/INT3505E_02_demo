import uuid
from datetime import datetime

from app.models import PaymentDB


STATUS_EVENT_MAP = {
    "PENDING": "payment.pending",
    "SUCCEEDED": "payment.succeeded",
    "FAILED": "payment.failed",
    "REFUNDED": "payment.refunded",
    "EXPIRED": "payment.expired",
}


def map_status_to_event_type(status: str) -> str:
    # fallback: nếu status lạ thì vẫn trả ra cho khỏi crash
    return STATUS_EVENT_MAP.get(status, f"payment.{status.lower()}")
    

def build_payment_event_payload(payment: PaymentDB, event_type: str) -> dict:
    event_id = f"evt_{uuid.uuid4().hex}"
    created_at = datetime.utcnow().isoformat() + "Z"

    return {
        "event_id": event_id,
        "event_type": event_type,
        "created_at": created_at,
        "data": {
            "payment_id": payment.id,
            "booking_id": payment.booking_id,
            "user_id": payment.user_id,
            "amount": float(payment.amount),
            "currency": payment.currency,
            "status": payment.status,
            "provider": payment.provider,
            "method": payment.method,
            "paid_at": payment.paid_at.isoformat() + "Z" if payment.paid_at else None,
            "expired_at": payment.expired_at.isoformat() + "Z" if payment.expired_at else None,
        },
    }
