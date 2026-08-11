from typing import Optional

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
    name: Optional[str]
    first_surname: Optional[str]
    second_surname: Optional[str]
    email: EmailStr
    created_at: str
    status: int


class UserByIdGlobalResponse(BaseModel):
    role: str
    id: int
    parking_id: str
    name: Optional[str]
    first_surname: Optional[str]
    second_surname: Optional[str]
    email: EmailStr
    created_at: str
    status: int


class UserByEmailResponse(BaseModel):
    role: str
    parking_id: Optional[str] = None
    id: int
    name: Optional[str] = None
    first_surname: Optional[str] = None
    second_surname: Optional[str] = None
    email: EmailStr
    password: Optional[str] = None
    onboarding_completed: int
    provider: ProviderType
    google_id: Optional[str] = None


class UserStatsResponse(BaseModel):
    total: int
    active: int
    disabled: int
    created_this_week: int


class SurnameResponse(BaseModel):
    surname: str
