from datetime import date, datetime, time
from typing import Optional
from pydantic import BaseModel, EmailStr


class ReservationsResponse(BaseModel):
    uuid: str
    name: str
    level: int
    email: EmailStr
    start_date: date
    start_time: time
    end_date: Optional[date] = None
    end_time: Optional[time] = None
    created_at: datetime
    status: int
