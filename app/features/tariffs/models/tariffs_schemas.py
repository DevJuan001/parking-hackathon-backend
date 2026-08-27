from pydantic import BaseModel


class CreateTariffSchema(BaseModel):
    vehicle_type: int
    value: float


class UpdateTariffSchema(BaseModel):
    vehicle_type: int | None = None
    value: float | None = None
