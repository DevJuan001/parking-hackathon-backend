from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi_limiter.depends import RateLimiter

from app.features.reservations.controllers.reservations_controller import (
    ReservationsController,
)
from app.features.reservations.models.reservations_schemas import (
    CreateReservationSchema,
    CreateSelfReservationSchema,
    FilterReservationsSchema,
    UpdateReservationSchema,
)
from app.middlewares.jwt_middleware import AuthPayload
from app.middlewares.onboarding_middleware import require_onboarded
from app.middlewares.roles_middleware import require_roles

router = APIRouter(prefix="/api/reservations", tags=["Reservations"])


@router.get(
    "/",
    dependencies=[
        Depends(require_roles(["Admin"])),
        Depends(RateLimiter(times=30, seconds=60)),
    ],
)
def get_all_reservations(
    filters: Annotated[FilterReservationsSchema, Query()], payload: AuthPayload
):
    return ReservationsController.get_all_reservations(filters, payload)


@router.post(
    "/create",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
        Depends(require_onboarded),
    ],
)
def create_reservation(data: CreateReservationSchema, payload: AuthPayload):
    return ReservationsController.create_reservation_for_user(data, payload)


@router.post(
    "/create-self",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
    ],
)
def create_self_reservation(
    data: CreateSelfReservationSchema,
):
    return ReservationsController.create_reservation_for_self(data)


@router.put(
    "/update/{reservation_id}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
        Depends(require_onboarded),
    ],
)
def update_reservation(
    reservation_id: str, data: UpdateReservationSchema, payload: AuthPayload
):
    return ReservationsController.update_reservation(reservation_id, data, payload)


@router.delete(
    "/delete/{reservation_id}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
        Depends(require_onboarded),
    ],
)
def delete_reservation(reservation_id: str, payload: AuthPayload):
    return ReservationsController.delete_reservation(reservation_id, payload)
