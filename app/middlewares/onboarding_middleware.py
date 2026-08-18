from fastapi import HTTPException

from app.middlewares.jwt_payload import JWTPayload


def require_onboarded(payload: JWTPayload) -> JWTPayload:
    if not payload.onboarding_completed:
        raise HTTPException(
            status_code=403,
            detail="Debes completar el onboarding para acceder a este recurso"
        )

    return payload
