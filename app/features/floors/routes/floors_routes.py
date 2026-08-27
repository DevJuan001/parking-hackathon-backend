from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter

from app.features.floors.controllers.floors_controller import FloorsController
from app.features.floors.models.floors_schemas import (
    CreateFloorSchema,
    UpdateFloorSchema,
)
from app.middlewares.jwt_middleware import AuthPayload

router = APIRouter(prefix="/api/floors", tags=["Floors"])


@router.get(
    "/",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
    ],
)
def get_all_floors(payload: AuthPayload):
    return FloorsController.get_all_floors(payload)


@router.get(
    "/{floor_id}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
    ],
)
def get_floor_by_id(floor_id: int, payload: AuthPayload):
    return FloorsController.get_floor_by_id(floor_id, payload)


@router.post(
    "/create",
    dependencies=[
        Depends(RateLimiter(times=10, seconds=60)),
    ],
)
def create_floor(floor_data: CreateFloorSchema, payload: AuthPayload):
    return FloorsController.create_floor(floor_data, payload)


@router.put(
    "/update/{floor_id}",
    dependencies=[
        Depends(RateLimiter(times=10, seconds=60)),
    ],
)
def update_floor(floor_id: int, floor_data: UpdateFloorSchema, payload: AuthPayload):
    return FloorsController.update_floor(floor_id, floor_data, payload)


@router.delete(
    "/delete/{floor_id}",
    dependencies=[
        Depends(RateLimiter(times=10, seconds=60)),
    ],
)
def delete_floor(floor_id: int, payload: AuthPayload):
    return FloorsController.delete_floor(floor_id, payload)
