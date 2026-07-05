from typing import Optional
from pydantic import BaseModel


class ExitsFiltersSchema(BaseModel):
    plate_id: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class CreateExitSchema(BaseModel):
    plate: str
