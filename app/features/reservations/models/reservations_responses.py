from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ReservationsResponse(BaseModel):
    id: int
    user_id: int
    name: str
    level: int
    start_date: datetime
    end_date: Optional[datetime] = None
    created_at: datetime
    status: int
