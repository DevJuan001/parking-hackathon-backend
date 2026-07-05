from typing import Optional
from pydantic import BaseModel

from app.utils.safe_types import safe_optional_str, safe_str


class SpotsFiltersSchema(BaseModel):
    spot_status: Optional[int] = None
    floor_id: Optional[int] = None


class CreateSpotSchema(BaseModel):
    floor_id: int
    spot: str = safe_str(min_length=1, max_length=100)
    vehicle_type_id: int


class UpdateSpotStatusSchema(BaseModel):
    spot_status: int


class UpdateSpotSchema(BaseModel):
    floor_id: Optional[int] = None
    spot: Optional[str] = safe_optional_str(min_length=1, max_length=100)
    spot_status: Optional[int] = None
    vehicle_type_id: Optional[int] = None
