from pydantic import BaseModel


class PlateResponse(BaseModel):
    id: int
    plate: str
    vehicle_type: int
    created_at: str


class SpotResponse(BaseModel):
    spot_id: int
    spot: str
    status: int


class VehicleTypeResponse(BaseModel):
    id: int
    name: str


class ParkingSummaryResponse(BaseModel):
    plate: str
    user_name: str
    vehicle_type: str
    entry_time: str
    exit_time: str
    time_parked: str
    payment_value: float
