from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from app.utils.safe_types import safe_optional_str, safe_str


class UsersFiltersSchema(BaseModel):
    role_order: Optional[int] = None
    first_surname: Optional[str] = safe_optional_str(
        min_length=1, max_length=256
    )
    name_order: Optional[str] = safe_optional_str(
        min_length=1, max_length=256
    )
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    page: int = Field(1, ge=1)
    per_page: int = Field(15, ge=1, le=100)


class CreateUserSchema(BaseModel):
    role_id: int
    name: str = safe_str(min_length=1, max_length=128)
    first_surname: str = safe_str(min_length=1, max_length=128)
    second_surname: str = safe_str(min_length=1, max_length=128)
    email: EmailStr = safe_str(max_length=254)


class CompleteUserOnboardingSchema(BaseModel):
    name: str = safe_str(min_length=1, max_length=128)
    first_surname: str = safe_str(min_length=1, max_length=128)
    second_surname: Optional[str] = safe_optional_str(
        min_length=1, max_length=256
    )


class UpdateUserSchema(BaseModel):
    role_id: Optional[int] = None
    name: Optional[str] = safe_optional_str(
        min_length=1, max_length=256
    )
    first_surname: Optional[str] = safe_optional_str(
        min_length=1, max_length=256
    )
    second_surname: Optional[str] = safe_optional_str(
        min_length=1, max_length=256
    )
    email: Optional[EmailStr] = safe_optional_str(
        max_length=256
    )


class UpdateCurrentUserSchema(BaseModel):
    name: Optional[str] = safe_optional_str(
        min_length=1, max_length=256
    )
    first_surname: Optional[str] = safe_optional_str(
        min_length=1, max_length=256
    )
    second_surname: Optional[str] = safe_optional_str(
        min_length=1, max_length=256
    )
    email: Optional[EmailStr] = safe_optional_str(
        max_length=256
    )


class UpdatePasswordSchema(BaseModel):
    old_password: str = safe_str(min_length=8, max_length=128)
    new_password: str = safe_str(min_length=8, max_length=128)
    repeat_password: str = safe_str(min_length=8, max_length=128)
