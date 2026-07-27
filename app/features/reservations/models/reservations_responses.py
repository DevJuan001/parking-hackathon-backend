from datetime import datetime
from pydantic import BaseModel


class ReservationsResponse(BaseModel):
    id: int
    name: str
    level: int
    start_date: datetime
    end_date: datetime
    created_at: datetime
    status: int
