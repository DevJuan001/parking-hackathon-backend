from datetime import date, datetime, time

from pydantic import BaseModel, EmailStr, Field

from app.utils.safe_types import safe_optional_str, safe_str


class FilterReservationsSchema(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    page: int = Field(1, ge=1)
    per_page: int = Field(50, ge=1, le=100)


class CreateReservationSchema(BaseModel):
    name: str = safe_str(min_length=1, max_length=100)
    plate: str = safe_str(min_length=6, max_length=6)
    email: EmailStr = safe_str(max_length=254)
    level: int = Field(..., ge=1)
    start_date: date
    start_time: time
    end_date: date | None = None
    end_time: time | None = None


class CreateSelfReservationSchema(BaseModel):
    parking_id: str = safe_str(min_length=1, max_length=36)
    name: str = safe_str(min_length=1, max_length=100)
    plate: str = safe_str(min_length=6, max_length=6)
    email: EmailStr = safe_str(max_length=254)
    level: int = Field(..., ge=1)
    start_date: date
    start_time: time
    end_date: date | None = None
    end_time: time | None = None


class UpdateReservationSchema(BaseModel):
    name: str | None = safe_optional_str(min_length=1, max_length=100)
    level: int | None = None
    email: EmailStr | None = safe_optional_str(max_length=254)
    start_date: date | datetime = None
    start_time: time | None = None
    end_date: date | datetime = None
    end_time: time | None = None
    status: int | None = None
