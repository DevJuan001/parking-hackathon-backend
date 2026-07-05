from typing import Optional
from pydantic import BaseModel, EmailStr


class LoginModelSchema(BaseModel):
    email: EmailStr
    password: str


class RecoverPasswordSchema(BaseModel):
    email: EmailStr


class VerifyRoleModelSchema(BaseModel):
    roles: list[str]


class RegisterSchema(BaseModel):
    email: EmailStr
    password: str
    repeat_password: str


class OnboardingSchema(BaseModel):
    name: str
    first_surname: str
    second_surname: Optional[str] = None
    parking_name: str
    parking_country: int
