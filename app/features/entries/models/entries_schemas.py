from datetime import date

from pydantic import BaseModel, Field

from app.utils.safe_types import safe_str


class EntriesFiltersSchema(BaseModel):
    plate_id: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    page: int = Field(1, ge=1)
    per_page: int = Field(15, ge=1, le=100)


class CreateEntrySchema(BaseModel):
    plate: str = safe_str(min_length=6, max_length=6)
