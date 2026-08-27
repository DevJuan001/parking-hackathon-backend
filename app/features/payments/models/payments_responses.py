from datetime import date, datetime

from pydantic import BaseModel


class PaymentResponse(BaseModel):
    uuid: str
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


class CountPaymentsStatsResponse(BaseModel):
    total: float
    today: float
    this_week: float
    this_month: float
