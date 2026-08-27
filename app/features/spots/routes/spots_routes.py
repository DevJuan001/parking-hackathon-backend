from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi_limiter.depends import RateLimiter

from app.features.spots.controllers.spots_controller import SpotsController
from app.features.spots.models.spots_schemas import (
    CreateSpotSchema,
    SpotsFiltersSchema,
    UpdateSpotSchema,
    UpdateSpotStatusSchema,
)
from app.middlewares.jwt_middleware import AuthPayload

router = APIRouter(prefix="/api/spots", tags=["Spots"])


@router.get(
    "/",
    dependencies=[
        Depends(RateLimiter(times=300, seconds=60)),
    ],
)
def get_all_spots(
    filters: Annotated[SpotsFiltersSchema, Query()], payload: AuthPayload
):
    return SpotsController.get_all_spots(filters, payload)


@router.get(
    "/{spot_id}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
    ],
)
def get_spot_by_id(spot_id: int, payload: AuthPayload):
    return SpotsController.get_spot_by_id(spot_id, payload)


@router.post(
    "/create",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
    ],
)
def create_spot(spot_data: CreateSpotSchema, payload: AuthPayload):
    return SpotsController.create_spot(spot_data, payload)


@router.put(
    "/{spot_id}/status",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
    ],
)
def update_spot_status(
    spot_id: int, status_data: UpdateSpotStatusSchema, payload: AuthPayload
):
    return SpotsController.update_spot_status(spot_id, status_data, payload)


@router.put(
    "/update/{spot_id}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
    ],
)
def update_spot(spot_id: int, spot_data: UpdateSpotSchema, payload: AuthPayload):
    return SpotsController.update_spot(spot_id, spot_data, payload)


@router.delete(
    "/delete/{spot_id}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
    ],
)
def delete_spot(spot_id: int, payload: AuthPayload):
    return SpotsController.delete_spot(spot_id, payload)
