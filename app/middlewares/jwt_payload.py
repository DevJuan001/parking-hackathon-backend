

from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel

from app.middlewares.jwt_middleware import verify_jwt


class JWTPayload(BaseModel):
    user_id: int
    role: str
    parking_id: str | None = None
    onboarding_completed: bool = False


AuthPayload = Annotated[JWTPayload, Depends(verify_jwt)]
