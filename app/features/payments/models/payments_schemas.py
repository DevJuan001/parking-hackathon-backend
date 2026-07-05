
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PaymentsFiltersSchema(BaseModel):
    plate_id: Optional[int] = None
    spot_id: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class CreatePaymentSchema(BaseModel):
    plate: str
    exit_time: datetime
    payment_method: int


class CalculatePaymentSchema(BaseModel):
    plate: str
