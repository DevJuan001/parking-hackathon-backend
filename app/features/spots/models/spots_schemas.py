
from pydantic import BaseModel, Field

from app.utils.safe_types import safe_optional_str, safe_str


class SpotsFiltersSchema(BaseModel):
    spot_status: int | None = None
    floor_id: int | None = None
    page: int = Field(1, ge=1)
    per_page: int = Field(56, ge=1, le=100)


class CreateSpotSchema(BaseModel):
    floor_id: int
    spot: str = safe_str(min_length=1, max_length=100)
    vehicle_type_id: int


class UpdateSpotStatusSchema(BaseModel):
    spot_status: int


class UpdateSpotSchema(BaseModel):
    floor_id: int | None = None
    spot: str | None = safe_optional_str(min_length=1, max_length=100)
    spot_status: int | None = None
    vehicle_type_id: int | None = None
