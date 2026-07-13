from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter
from app.middlewares.jwt_middleware import verify_jwt
from app.middlewares.roles_middleware import require_roles
from app.middlewares.onboarding_middleware import require_onboarded
from app.features.entries.controllers.entries_controller import EntriesController
from app.features.entries.models.entries_schemas import CreateEntrySchema, EntriesFiltersSchema

router = APIRouter(
    prefix="/api/entries",
    tags=["Entries"]
)


@router.get(
    "/",
    dependencies=[
        Depends(RateLimiter(times=100, seconds=60)),
        Depends(require_roles(["Admin"])),
        Depends(require_onboarded)
    ]
)
def get_all_entries(
    filters: EntriesFiltersSchema = Depends(),
    payload: dict = Depends(verify_jwt)
):
    return EntriesController.get_all_entries(filters, payload)


@router.get(
    "/recent-entries",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
        Depends(require_onboarded)
    ]
)
def get_recent_entries(payload: dict = Depends(verify_jwt)):
    return EntriesController.get_recent_entries(payload)


@router.get(
    "/by-stats",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
        Depends(require_onboarded)
    ]
)
def get_entry_stats(payload: dict = Depends(verify_jwt)):
    return EntriesController.get_entry_stats(payload)


@router.get(
    "/plate/{plate_id}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
        Depends(require_onboarded)
    ]
)
def get_entries_by_plate(
    plate_id: int,
    payload: dict = Depends(verify_jwt)
):
    return EntriesController.get_entries_by_plate(plate_id, payload)


@router.get(
    "/{entry_id}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
        Depends(require_onboarded)
    ]
)
def get_entry_by_id(
    entry_id: int,
    payload: dict = Depends(verify_jwt)
):
    return EntriesController.get_entry_by_id(entry_id, payload)


@router.post(
    "/create",
    dependencies=[
        Depends(require_roles(["Admin", "Cliente"])),
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_onboarded)
    ]
)
async def create_entry(
    entry_data: CreateEntrySchema,
    payload: dict = Depends(verify_jwt)
):
    return await EntriesController.create_entry(entry_data, payload)
