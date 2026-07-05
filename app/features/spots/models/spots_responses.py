from typing import Optional
from pydantic import BaseModel


class SpotResponse(BaseModel):
    spot_id: int
    floor_id: int
    spot: str
    spot_status: int
    created_at: str
    vehicle_type_id: int
    plate: Optional[str] = None
