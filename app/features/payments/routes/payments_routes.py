from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter
from app.middlewares.jwt_middleware import verify_jwt
from app.middlewares.roles_middleware import require_roles
from app.features.payments.controllers.payments_controller import PaymentsController
from app.features.payments.models.payments_schemas import CreatePaymentSchema, PaymentsFiltersSchema, CalculatePaymentSchema

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
    filters: PaymentsFiltersSchema = Depends(),
    payload: dict = Depends(verify_jwt)
):
    return PaymentsController.get_all_payments(filters, payload)


@router.get(
    "/calculate/",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Cliente"])),
    ]
)
def calculate_payment(
    params: CalculatePaymentSchema = Depends(),
    payload: dict = Depends(verify_jwt)
):
    return PaymentsController.calculate_payment(params, payload)


@router.get(
    "/payment-methods",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin", "Cliente"])),
    ]
)
def get_all_payment_methods(payload: dict = Depends(verify_jwt)):
    return PaymentsController.get_all_payment_methods(payload)


@router.get(
    "/growth/{period}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ]
)
def get_payments_growth(
    period: str = "30d",
    payload: dict = Depends(verify_jwt)
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
    payload: dict = Depends(verify_jwt)
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
    payload: dict = Depends(verify_jwt)
):
    return PaymentsController.get_payment_by_id(payment_id, payload)


@router.post(
    "/create",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Cliente"])),
    ]
)
async def create_payment(
    payment_data: CreatePaymentSchema,
    payload: dict = Depends(verify_jwt)
):
    return await PaymentsController.create_payment(payment_data, payload)
