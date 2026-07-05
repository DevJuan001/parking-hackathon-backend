from typing import Optional
from pydantic import BaseModel


class CreateTariffSchema(BaseModel):
    vehicle_type: int
    value: float


class UpdateTariffSchema(BaseModel):
    vehicle_type: Optional[int] = None
    value: Optional[float] = None
