from datetime import UTC, date, datetime, time, timedelta
from typing import Literal

from pydantic import BaseModel, field_validator


class TimeRemaining(BaseModel):
    value: int
    unit: Literal["months", "days", "hours"]


class ParkingResponse(BaseModel):
    uuid: str
    name: str
    address: str


class ParkingPrivateResponse(BaseModel):
    uuid: str
    name: str
    address: str
    start_day: int
    start_time: time
    end_day: int
    end_time: time
    plan: str
    plan_value: float
    next_payment_at: date | None = None
    time_remaining: TimeRemaining | None = None

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def _coerce_time(cls, value):
        # mysql-connector-python devuelve TIME como timedelta; Pydantic time lo rechaza.
        if isinstance(value, timedelta):
            return (datetime(1970, 1, 1, tzinfo=UTC) + value).time()
        return value


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
