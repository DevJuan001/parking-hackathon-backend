from fastapi import APIRouter, Depends, Request, Response
from fastapi_limiter.depends import RateLimiter

from app.features.auth.controllers.auth_controller import AuthController
from app.features.auth.models.auth_schema import (
    LoginModelSchema,
    OnboardingSchema,
    RecoverPasswordSchema,
    RegisterSchema,
    VerifyRoleModelSchema,
)
from app.middlewares.jwt_middleware import verify_jwt
from app.middlewares.roles_middleware import require_roles


router = APIRouter(
    prefix="/api/auth",
    tags=["Auth"]
)


# Endpoint para loguearse
@router.post(
    "/login",
    dependencies=[
        Depends(RateLimiter(times=10, seconds=60))
    ]
)
def login(credentials: LoginModelSchema, response: Response):
    return AuthController.login(credentials.email, credentials.password, response)


# Endpoint para registrar un nuevo administrador
@router.post(
    "/register",
    dependencies=[
        Depends(RateLimiter(times=3, seconds=60))
    ]
)
async def register(data: RegisterSchema, response: Response):
    return await AuthController.register(data, response)


# Endpoint para completar el onboarding
@router.put(
    "/complete-on-boarding",
    dependencies=[
        Depends(RateLimiter(times=5, seconds=60)),
        Depends(require_roles(["Admin"]))
    ]
)
async def complete_onboarding(
    data: OnboardingSchema,
    payload: dict = Depends(verify_jwt),
    response: Response = None
):
    return await AuthController.complete_onboarding(data, payload, response)


# Endpoint para actualizar el token de acceso
@router.post(
    "/refresh",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
    ]
)
async def refresh_tokens(request: Request, response: Response):
    return await AuthController.refresh_tokens(request, response)


# Endpoint para cerrar sesión
@router.post("/logout")
def logout(response: Response):
    return AuthController.logout(response)


# Endpoint para recuperar contraseña
@router.post(
    "/recover-password",
    dependencies=[
        Depends(RateLimiter(times=3, seconds=60)),
    ]
)
async def recover_password(data: RecoverPasswordSchema):
    return await AuthController.recover_password(data.email)
