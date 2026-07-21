from datetime import datetime
from pydantic import BaseModel, Field


class ExitResponse(BaseModel):
    id: int
    plate: str
    value: int
    payment_method: str = "No registrado"
    created_at: datetime


class ExitStatsResponse(BaseModel):
    total_exits: int
    today_exits: int
    this_week_exits: int
    this_month_exits: int
    total_revenue: int
    today_revenue: int
    this_week_revenue: int
    this_month_revenue: int
