
import datetime
from datetime import date, time, datetime
from typing import Optional, Union
from pydantic import BaseModel, Field

from app.utils.safe_types import safe_optional_str, safe_str


class FilterReservationsSchema(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    page: int = Field(1, ge=1)
    per_page: int = Field(50, ge=1, le=100)


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


class UpdateReservationSchema(BaseModel):
    name: Optional[str] = safe_optional_str(min_length=1, max_length=100)
    client_id: Optional[int] = None
    level: Optional[int] = None
    start_date: Union[date, datetime] = None
    start_time: Optional[time] = None
    end_date: Union[date, datetime] = None
    end_time: Optional[time] = None
    status: Optional[int] = None
