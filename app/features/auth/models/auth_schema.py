from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from app.utils.safe_types import safe_optional_str, safe_str


class LoginModelSchema(BaseModel):
    email: EmailStr = safe_str(max_length=254)
    password: str = Field(..., min_length=8, max_length=128)


class RecoverPasswordSchema(BaseModel):
    email: EmailStr = safe_str(max_length=254)


class RegisterSchema(BaseModel):
    email: EmailStr = safe_str(max_length=254)
    password: str = Field(..., min_length=8, max_length=128)
    repeat_password: str = Field(..., min_length=8, max_length=128)


class OnboardingSchema(BaseModel):
    name: str = safe_str(min_length=3, max_length=100)
    first_surname: str = safe_str(min_length=3, max_length=100)
    second_surname: Optional[str] = safe_optional_str(max_length=100)
    parking_name: str = safe_str(min_length=3, max_length=100)
    parking_country: int
