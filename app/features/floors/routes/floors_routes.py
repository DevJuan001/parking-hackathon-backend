from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter
from app.middlewares.jwt_middleware import verify_jwt
from app.features.floors.controllers.floors_controller import FloorsController
from app.features.floors.models.floors_schemas import (
    CreateFloorSchema,
    UpdateFloorSchema
)

router = APIRouter(
    prefix="/api/floors",
    tags=["Floors"]
)


@router.get(
    "/",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(verify_jwt)
    ]
)
def get_all_floors(payload: dict = Depends(verify_jwt)):
    return FloorsController.get_all_floors(payload)


@router.get(
    "/{floor_id}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(verify_jwt)
    ]
)
def get_floor_by_id(
    floor_id: int,
    payload: dict = Depends(verify_jwt)
):
    return FloorsController.get_floor_by_id(floor_id, payload)


@router.post(
    "/create",
    dependencies=[
        Depends(RateLimiter(times=10, seconds=60)),
        Depends(verify_jwt)
    ]
)
def create_floor(
    floor_data: CreateFloorSchema,
    payload: dict = Depends(verify_jwt)
):
    return FloorsController.create_floor(floor_data, payload)


@router.put(
    "/update/{floor_id}",
    dependencies=[
        Depends(RateLimiter(times=10, seconds=60)),
        Depends(verify_jwt)
    ]
)
def update_floor(
    floor_id: int,
    floor_data: UpdateFloorSchema,
    payload: dict = Depends(verify_jwt)
):
    return FloorsController.update_floor(floor_id, floor_data, payload)


@router.delete(
    "/delete/{floor_id}",
    dependencies=[
        Depends(RateLimiter(times=10, seconds=60)),
        Depends(verify_jwt)
    ]
)
def delete_floor(
    floor_id: int,
    payload: dict = Depends(verify_jwt)
):
    return FloorsController.delete_floor(floor_id, payload)
