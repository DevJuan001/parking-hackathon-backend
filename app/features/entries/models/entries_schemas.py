from typing import Optional
from pydantic import BaseModel


class EntriesFiltersSchema(BaseModel):
    plate_id: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class CreateEntrySchema(BaseModel):
    plate: str
