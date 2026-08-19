from typing import Annotated

from fastapi import Depends, HTTPException

from app.middlewares.jwt_middleware import verify_jwt
from app.middlewares.jwt_payload import JWTPayload


def require_onboarded(payload: Annotated[JWTPayload, Depends(verify_jwt)]) -> JWTPayload:
    if not payload.onboarding_completed:
        raise HTTPException(
            status_code=403,
            detail="Debes completar el onboarding para acceder a este recurso"
        )

    return payload
