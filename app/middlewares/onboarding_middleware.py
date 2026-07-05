from fastapi import Depends, HTTPException

from app.middlewares.jwt_middleware import verify_jwt


def require_onboarded(payload: dict = Depends(verify_jwt)):
    if not payload.get("onboarding_completed"):
        raise HTTPException(
            status_code=403,
            detail="Debes completar el onboarding para acceder a este recurso"
        )

    return payload
