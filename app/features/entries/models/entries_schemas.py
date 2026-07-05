from datetime import date
from typing import Optional
from pydantic import BaseModel

from app.utils.safe_types import safe_str


class EntriesFiltersSchema(BaseModel):
    plate_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class CreateEntrySchema(BaseModel):
    plate: str = safe_str(min_length=6, max_length=6)
