
from pydantic import BaseModel, EmailStr

from app.features.users.types.users_types import ProviderType


class UserResponse(BaseModel):
    role_id: int
    role_name: str
    id: int
    name: str
    first_surname: str
    second_surname: str
    email: EmailStr
    created_at: str
    status: int


class UserByIdResponse(BaseModel):
    role: str
    id: int
    name: str | None
    first_surname: str | None
    second_surname: str | None
    email: EmailStr
    created_at: str
    status: int


class UserByIdGlobalResponse(BaseModel):
    role: str
    id: int
    parking_id: str | None = None
    name: str | None
    first_surname: str | None
    second_surname: str | None
    email: EmailStr
    created_at: str
    status: int


class UserByEmailResponse(BaseModel):
    role: str
    parking_id: str | None = None
    id: int
    name: str | None = None
    first_surname: str | None = None
    second_surname: str | None = None
    email: EmailStr
    password: str | None = None
    onboarding_completed: int
    provider: ProviderType
    google_id: str | None = None


class UserStatsResponse(BaseModel):
    total: int
    active: int
    disabled: int
    created_this_week: int


class SurnameResponse(BaseModel):
    surname: str
