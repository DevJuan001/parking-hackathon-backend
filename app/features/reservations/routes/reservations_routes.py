from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter

from app.middlewares.jwt_middleware import verify_jwt
from app.middlewares.roles_middleware import require_roles
from app.middlewares.onboarding_middleware import require_onboarded
from app.features.reservations.models.reservations_schema import (
    CreateReservationSchema,
    CreateSelfReservationSchema,
    FilterReservationsSchema,
    UpdateReservationSchema,
)
from app.features.reservations.controllers.reservations_controller import ReservationsController


router = APIRouter(
    prefix="/api/reservations",
    tags=["Reservations"]
)


@router.get(
    "/",
    dependencies=[
        Depends(require_roles(["Admin"])),
        Depends(RateLimiter(times=30, seconds=60))
    ]
)
def get_all_reservations(
    filters: FilterReservationsSchema = Depends(),
    payload: dict = Depends(verify_jwt)
):
    return ReservationsController.get_all_reservations(filters, payload)


@router.post(
    "/create",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
        Depends(require_onboarded),
    ]
)
def create_reservation(
    data: CreateReservationSchema,
    payload: dict = Depends(verify_jwt)
):
    return ReservationsController.create_reservation_for_user(data, payload)


@router.post(
    "/create-self",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Cliente"])),
        Depends(require_onboarded),
    ]
)
def create_self_reservation(
    data: CreateSelfReservationSchema,
    payload: dict = Depends(verify_jwt)
):
    return ReservationsController.create_reservation_for_self(data, payload)


@router.put(
    "/update/{reservation_id}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
        Depends(require_onboarded),
    ]
)
def update_reservation(
    reservation_id: int,
    data: UpdateReservationSchema,
    payload: dict = Depends(verify_jwt)
):
    return ReservationsController.update_reservation(reservation_id, data, payload)
