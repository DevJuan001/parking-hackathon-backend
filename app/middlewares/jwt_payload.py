

from pydantic import BaseModel


class JWTPayload(BaseModel):
    user_id: int
    role: str
    parking_id: str | None = None
    onboarding_completed: bool = False
