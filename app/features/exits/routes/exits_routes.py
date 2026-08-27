from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi_limiter.depends import RateLimiter

from app.features.exits.controllers.exits_controller import ExitsController
from app.features.exits.models.exits_schemas import (
    CreateExitSchema,
    ExitsFiltersSchema,
    StatsExitsFiltersSchema,
)
from app.middlewares.jwt_middleware import AuthPayload
from app.middlewares.roles_middleware import require_roles

router = APIRouter(
    prefix="/api/exits",
    tags=["Exits"]
)


@router.get(
    "/",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ]
)
def get_all_exits(
    filters: Annotated[ExitsFiltersSchema, Query()],
    payload: AuthPayload
):
    return ExitsController.get_all_exits(filters, payload)


@router.get(
    "/plate/{plate_id}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ]
)
def get_exits_by_plate(
    plate_id: int,
    payload: AuthPayload
):
    return ExitsController.get_exits_by_plate(plate_id, payload)


@router.get(
    "/stats/",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ]
)
def get_exit_stats(
    filters: Annotated[StatsExitsFiltersSchema, Query()],
    payload: AuthPayload
):
    return ExitsController.get_exit_stats(filters, payload)


@router.get(
    "/{exit_id}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ]
)
def get_exit_by_id(
    exit_id: int,
    payload: AuthPayload
):
    return ExitsController.get_exit_by_id(exit_id, payload)


@router.post(
    "/create",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
    ]
)
async def create_exit(
    exit_data: CreateExitSchema,
    payload: AuthPayload
):
    return await ExitsController.create_exit(exit_data, payload)
