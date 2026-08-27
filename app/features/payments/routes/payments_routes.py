from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi_limiter.depends import RateLimiter

from app.features.payments.controllers.payments_controller import PaymentsController
from app.features.payments.models.payments_schemas import (
    CalculatePaymentSchema,
    CreatePaymentSchema,
    PaymentsFiltersSchema,
)
from app.middlewares.jwt_middleware import AuthPayload
from app.middlewares.roles_middleware import require_roles

router = APIRouter(
    prefix="/api/payments",
    tags=["Payments"]
)


@router.get(
    "/",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ]
)
def get_all_payments(
    filters: Annotated[PaymentsFiltersSchema, Query()],
    payload: AuthPayload
):
    return PaymentsController.get_all_payments(filters, payload)


@router.get(
    "/calculate/",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Maquina"])),
    ]
)
def calculate_payment(
    params: Annotated[CalculatePaymentSchema, Query()],
    payload: AuthPayload
):
    return PaymentsController.calculate_payment(params, payload)


@router.get(
    "/payment-methods",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin", "Maquina"])),
    ]
)
def get_all_payment_methods():
    return PaymentsController.get_all_payment_methods()


@router.get(
    "/growth/{period}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ]
)
def get_payments_growth(
    period: str,
    payload: AuthPayload
):
    return PaymentsController.get_payments_growth(period, payload)


@router.get(
    "/plate/{plate_id}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ]
)
def get_payments_by_plate(
    plate_id: int,
    payload: AuthPayload
):
    return PaymentsController.get_payments_by_plate(plate_id, payload)


@router.get(
    "/{payment_id}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ]
)
def get_payment_by_id(
    payment_id: int,
    payload: AuthPayload
):
    return PaymentsController.get_payment_by_id(payment_id, payload)


@router.post(
    "/create",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Maquina"])),
    ]
)
async def create_payment(
    payment_data: CreatePaymentSchema,
    payload: AuthPayload
):
    return await PaymentsController.create_payment(payment_data, payload)
