from datetime import time
from typing import Optional
from pydantic import BaseModel

from app.utils.safe_types import safe_str, safe_optional_str


class CreatePlateSchema(BaseModel):
    plate: str = safe_str(min_length=6, max_length=6)


class FindPlateSchema(BaseModel):
    plate: str = safe_str(min_length=6, max_length=6)


class UpdateParkingSchema(BaseModel):
    name: Optional[str] = safe_optional_str(min_length=1, max_length=100)
    address: Optional[str] = safe_optional_str(min_length=1, max_length=256)
    start_day: Optional[int] = None
    start_time: Optional[time] = None
    end_day: Optional[int] = None
    end_time: Optional[time] = None
