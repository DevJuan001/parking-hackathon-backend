from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi_limiter.depends import RateLimiter

from app.features.parking.controllers.parking_controller import ParkingController
from app.features.parking.models.parking_schemas import (
    CreatePlateSchema,
    UpdateParkingSchema,
)
from app.features.spots.models.spots_schemas import SpotsFiltersSchema
from app.middlewares.jwt_middleware import AuthPayload
from app.middlewares.roles_middleware import require_roles

router = APIRouter(
    prefix="/api/parking",
    tags=["Parking"]
)


@router.get(
    "/me/private-info",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ]
)
def get_parking_by_private_info(payload: AuthPayload):
    return ParkingController.get_parking_by_private_info(payload)


@router.get(
    "/plates",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ]
)
def get_all_plates(payload: AuthPayload):
    return ParkingController.get_all_plates(payload)


@router.get(
    "/vehicle-types",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ]
)
def get_all_vehicle_types():
    return ParkingController.get_all_vehicle_types()


@router.get(
    "/spots",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ]
)
def get_all_spots(
    filters: Annotated[SpotsFiltersSchema, Query()],
    payload: AuthPayload
):
    return ParkingController.get_all_spots(payload, filters)


@router.get(
    "/plates/find/{plate}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ]
)
def get_plate_by_name(plate: str, payload: AuthPayload):
    return ParkingController.get_plate_by_name(plate, payload)


@router.get(
    "/{parking_id}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
    ]
)
def get_parking_by_id(parking_id: str):
    return ParkingController.get_parking_by_id(parking_id)


@router.post(
    "/plates/create",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ]
)
async def create_plate(
    plate_data: CreatePlateSchema,
    payload: AuthPayload
):
    return await ParkingController.create_plate(plate_data, payload)


@router.put(
    "/update/me",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ]
)
def update_parking(
    data: UpdateParkingSchema,
    payload: AuthPayload
):
    return ParkingController.update_parking(data, payload)
