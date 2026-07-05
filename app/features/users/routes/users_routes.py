from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter
from app.middlewares.jwt_middleware import verify_jwt
from app.middlewares.roles_middleware import require_roles
from app.features.users.controllers.users_controller import UsersController
from app.features.users.models.users_schemas import CreateUserSchema, UpdateCurrentUserSchema, UpdatePasswordSchema, UpdateUserSchema, UsersFiltersSchema

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


# Endpoint para obtener todos los usuarios
@router.get(
    "/",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"]))
    ]
)
def get_all_users(
    filters: UsersFiltersSchema = Depends(),
    payload: dict = Depends(verify_jwt)
):
    return UsersController.get_all_users(filters, payload)


# Endpoint para obtener la información del usuario autenticado
@router.get(
    "/me",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin", "Cliente"])),
    ]
)
def get_me(payload: dict = Depends(verify_jwt)):
    return UsersController.get_current_user(payload)


# Endpoint para obtener todos los roles existentes
@router.get(
    "/roles",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"]))
    ]
)
def get_all_roles():
    return UsersController.get_all_roles()


# Endpoint para obtener los apellidos (first_surname) distintos del parking
@router.get(
    "/surnames",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"]))
    ]
)
def get_all_surnames(payload: dict = Depends(verify_jwt)):
    return UsersController.get_all_surnames(payload)


@router.get(
    "/by-stats",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"]))
    ]
)
def get_user_stats(payload: dict = Depends(verify_jwt)):
    return UsersController.get_user_stats(payload)


# Endpoint para obtener un usuario mediante el id
@router.get(
    "/{user_id}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"]))
    ]
)
def get_user_by_id(
    user_id: int,
    payload: dict = Depends(verify_jwt)
):
    return UsersController.get_user_by_id(user_id, payload)


# Endpoint para crear o registrar un usuario
@router.post(
    "/create",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ]
)
async def create_user(
    user_data: CreateUserSchema,
    payload: dict = Depends(verify_jwt)
):
    return await UsersController.create_user(user_data, payload)


# Endpoint para actualizar la informacion del usuario
@router.put(
    "/update/me",
    dependencies=[
        Depends(RateLimiter(times=10, seconds=60)),
        Depends(require_roles(["Admin", "Cliente"]))
    ]
)
def update_me(user_data: UpdateCurrentUserSchema, payload: dict = Depends(verify_jwt)):
    return UsersController.update_current_user(user_data, payload)


# Endpoint para actualizar la contraseña del usuario
@router.put(
    "/update-password",
    dependencies=[
        Depends(RateLimiter(times=10, seconds=60)),
        Depends(require_roles(["Admin", "Cliente"]))
    ]
)
def update_user_password(password_data: UpdatePasswordSchema, payload: dict = Depends(verify_jwt)):
    return UsersController.update_user_password(password_data, payload)


# Endpoint para actualizar la información de un usuario existente mediante su id
@router.put(
    "/update/{user_id}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"]))
    ]
)
def update_user(
    user_id: int,
    user_data: UpdateUserSchema,
    payload: dict = Depends(verify_jwt)
):
    return UsersController.update_user(user_id, user_data, payload)


# Endpoint para deshabilitar un usuario mediante su id
@router.put(
    "/disable/{user_id}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"]))
    ]
)
def disable_user(
    user_id: int,
    payload: dict = Depends(verify_jwt)
):
    return UsersController.disable_user(user_id, payload)


# Endpoint para habilitar un usuario mediante su id
@router.put(
    "/enable/{user_id}",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"]))
    ]
)
def enable_user(
    user_id: int,
    payload: dict = Depends(verify_jwt)
):
    return UsersController.enable_user(user_id, payload)
