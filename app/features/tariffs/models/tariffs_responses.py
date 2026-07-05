from pydantic import BaseModel


class TariffResponse(BaseModel):
    id: int
    vehicle_type: int
    value: float
    created_at: str
    updated_at: str
