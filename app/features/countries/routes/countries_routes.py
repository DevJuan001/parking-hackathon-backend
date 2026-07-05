from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter
from app.middlewares.roles_middleware import require_roles
from app.features.countries.controllers.countries_controller import CountriesController

router = APIRouter(
    prefix="/api/countries",
    tags=["Countries"]
)


@router.get(
    "/",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ]
)
def get_all_countries():
    return CountriesController.get_all_countries()
