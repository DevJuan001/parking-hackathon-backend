from datetime import date
from typing import Optional
from pydantic import BaseModel, Field

from app.utils.safe_types import safe_str


class ExitsFiltersSchema(BaseModel):
    plate_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    page: int = Field(1, ge=1)
    per_page: int = Field(15, ge=1, le=100)


class CreateExitSchema(BaseModel):
    plate: str = safe_str(min_length=6, max_length=6)
