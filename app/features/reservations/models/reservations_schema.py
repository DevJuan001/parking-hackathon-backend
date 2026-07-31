from datetime import date, time
from typing import Optional
from pydantic import BaseModel, Field

from app.utils.safe_types import safe_str


class FilterReservationsSchema(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class CreateReservationSchema(BaseModel):
    client_id: int = Field(..., ge=1)
    name: str = safe_str(min_length=1, max_length=100)
    level: int = Field(..., ge=1)
    start_date: date
    start_time: time
    end_date: Optional[date] = None
    end_time: Optional[time] = None


class CreateSelfReservationSchema(BaseModel):
    name: str = safe_str(min_length=1, max_length=100)
    level: int = Field(..., ge=1)
    start_date: date
    start_time: time
    end_date: Optional[date] = None
    end_time: Optional[time] = None
