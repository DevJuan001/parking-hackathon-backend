
from datetime import date, datetime

from pydantic import BaseModel

from app.utils.safe_types import safe_str


class PaymentsFiltersSchema(BaseModel):
    plate_id: int | None = None
    spot_id: int | None = None
    start_date: date | None = None
    end_date: date | None = None


class CreatePaymentSchema(BaseModel):
    plate: str = safe_str(min_length=6, max_length=6)
    exit_time: datetime
    payment_method: int


class CalculatePaymentSchema(BaseModel):
    plate: str = safe_str(min_length=6, max_length=6)
