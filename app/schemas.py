from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PaymentBase(BaseModel):
    booking_id: int
    user_id: int
    amount: float
    currency: str = "VND"
    provider: str
    method: str


class PaymentCreate(PaymentBase):
    """Input khi tạo mới payment.
    Status sẽ default là 'PENDING' trong DB, không cho client tự set.
    """
    pass


class PaymentRead(PaymentBase):
    id: int
    status: str
    paid_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True      

class PaymentStatusUpdate(BaseModel):
    new_status: str

class WebhookSubscriptionBase(BaseModel):
    target_url: str
    event_type: str
    is_active: bool = True
    secret: Optional[str] = None   


class WebhookSubscriptionCreate(WebhookSubscriptionBase):
    pass


class WebhookSubscriptionRead(WebhookSubscriptionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


