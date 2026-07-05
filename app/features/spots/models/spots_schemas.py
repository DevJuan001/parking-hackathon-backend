from typing import Optional
from pydantic import BaseModel


class SpotsFiltersSchema(BaseModel):
    spot_status: Optional[int] = None
    floor_id: Optional[int] = None


class CreateSpotSchema(BaseModel):
    floor_id: int
    spot: str
    vehicle_type_id: int


class UpdateSpotStatusSchema(BaseModel):
    spot_status: int


class UpdateSpotSchema(BaseModel):
    floor_id: Optional[int] = None
    spot: Optional[str] = None
    spot_status: Optional[int] = None
    vehicle_type_id: Optional[int] = None
