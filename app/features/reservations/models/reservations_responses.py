from datetime import date, datetime, time

from pydantic import BaseModel, EmailStr


class ReservationsResponse(BaseModel):
    uuid: str
    name: str
    level: int
    email: EmailStr
    start_date: date
    start_time: time
    end_date: date | None = None
    end_time: time | None = None
    created_at: datetime
    status: int
