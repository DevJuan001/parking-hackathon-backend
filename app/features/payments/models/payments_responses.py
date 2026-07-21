from datetime import datetime, date
from pydantic import BaseModel


class PaymentResponse(BaseModel):
    id: int
    plate: str
    spot: str
    value: float
    created_at: str
    payment_method: int


class PaymentMethodResponse(BaseModel):
    id: int
    name: str
    icon: str


class CalculatePaymentResponse(BaseModel):
    plate: str
    entry_time: datetime
    exit_time: datetime
    hours_parked: float
    rate_value: float
    total: float


class PaymentsGrowthResponse(BaseModel):
    date: date | str
    value: float
