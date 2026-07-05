
from typing import Optional
from pydantic import BaseModel
from datetime import date, datetime

from app.utils.safe_types import safe_str


class PaymentsFiltersSchema(BaseModel):
    plate_id: Optional[int] = None
    spot_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class CreatePaymentSchema(BaseModel):
    plate: str = safe_str(min_length=6, max_length=6)
    exit_time: datetime
    payment_method: int


class CalculatePaymentSchema(BaseModel):
    plate: str = safe_str(min_length=6, max_length=6)
