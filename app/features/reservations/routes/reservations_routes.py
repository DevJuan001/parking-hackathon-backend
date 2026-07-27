from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter

from app.middlewares.jwt_middleware import verify_jwt
from app.middlewares.roles_middleware import require_roles
from app.features.reservations.models.reservations_schema import FilterReservationsSchema
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
