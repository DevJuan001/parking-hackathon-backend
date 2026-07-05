from datetime import datetime
from pydantic import BaseModel, Field


class ExitResponse(BaseModel):
    id: int
    plate: str
    value: float = 0.0
    payment_method: str = "No registrado"
    created_at: datetime


class ExitStatsResponse(BaseModel):
    total_exits: int
    today_exits: int
    this_week_exits: int
    this_month_exits: int
    total_revenue: float
    today_revenue: float
    this_week_revenue: float
    this_month_revenue: float
