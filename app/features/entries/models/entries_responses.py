from datetime import datetime
from pydantic import BaseModel


class EntryResponse(BaseModel):
    id: int
    plate: str
    vehicle_type: int
    spot_id: int
    spot: str
    created_at: datetime


class EntryStatsResponse(BaseModel):
    total: int
    today: int
    this_week: int
    this_month: int
