
import datetime
from datetime import date, time, datetime
from typing import Optional, Union
from pydantic import BaseModel, EmailStr, Field

from app.utils.safe_types import safe_optional_str, safe_str


class FilterReservationsSchema(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    page: int = Field(1, ge=1)
    per_page: int = Field(50, ge=1, le=100)


class CreateReservationSchema(BaseModel):
    name: str = safe_str(min_length=1, max_length=100)
    plate: str = safe_str(min_length=6, max_length=6)
    email: EmailStr = safe_str(max_length=254)
    level: int = Field(..., ge=1)
    start_date: date
    start_time: time
    end_date: Optional[date] = None
    end_time: Optional[time] = None


class CreateSelfReservationSchema(BaseModel):
    parking_id: int = Field(..., ge=1)
    name: str = safe_str(min_length=1, max_length=100)
    plate: str = safe_str(min_length=6, max_length=6)
    email: EmailStr = safe_str(max_length=254)
    level: int = Field(..., ge=1)
    start_date: date
    start_time: time
    end_date: Optional[date] = None
    end_time: Optional[time] = None


class UpdateReservationSchema(BaseModel):
    name: Optional[str] = safe_optional_str(min_length=1, max_length=100)
    level: Optional[int] = None
    email: Optional[EmailStr] = safe_optional_str(max_length=254)
    start_date: Union[date, datetime] = None
    start_time: Optional[time] = None
    end_date: Union[date, datetime] = None
    end_time: Optional[time] = None
    status: Optional[int] = None
