from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter
from app.middlewares.jwt_middleware import verify_jwt
from app.middlewares.roles_middleware import require_roles
from app.features.tariffs.controllers.tariffs_controller import TariffsController
from app.features.tariffs.models.tariffs_schemas import CreateTariffSchema, UpdateTariffSchema

router = APIRouter(
    prefix="/api/tariffs",
    tags=["Tariffs"]
)


@router.get(
    "/",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ]
)
def get_all_tariffs(payload: dict = Depends(verify_jwt)):
    return TariffsController.get_all_tariffs(payload)


@router.get(
    "/available-vehicle-types",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ]
)
def get_available_vehicle_types(payload: dict = Depends(verify_jwt)):
    return TariffsController.get_available_vehicle_types(payload)


@router.get(
    "/{tariff_id}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ]
)
def get_tariff_by_id(
    tariff_id: int,
    payload: dict = Depends(verify_jwt)
):
    return TariffsController.get_tariff_by_id(tariff_id, payload)


@router.post(
    "/create",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ]
)
async def create_tariff(
    tariff_data: CreateTariffSchema,
    payload: dict = Depends(verify_jwt)
):
    return await TariffsController.create_tariff(tariff_data, payload)


@router.put(
    "/update/{tariff_id}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ]
)
def update_tariff(
    tariff_id: int,
    tariff_data: UpdateTariffSchema,
    payload: dict = Depends(verify_jwt)
):
    return TariffsController.update_tariff(tariff_id, tariff_data, payload)


@router.delete(
    "/delete/{tariff_id}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ]
)
def delete_tariff(
    tariff_id: int,
    payload: dict = Depends(verify_jwt)
):
    return TariffsController.delete_tariff(tariff_id, payload)
