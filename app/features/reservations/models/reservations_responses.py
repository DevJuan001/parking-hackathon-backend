from datetime import date, datetime, time
from typing import Optional
from pydantic import BaseModel


class ReservationsResponse(BaseModel):
    id: int
    user_id: int
    name: str
    level: int
    start_date: date
    start_time: time
    end_date: Optional[date] = None
    end_time: Optional[time] = None
    created_at: datetime
    status: int
