from typing import Optional
from pydantic import BaseModel, EmailStr


class UsersFiltersSchema(BaseModel):
    role_order: Optional[int] = None
    first_surname: Optional[str] = None
    name_order: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class CreateUserSchema(BaseModel):
    role_id: int
    name: str
    first_surname: str
    second_surname: str
    email: EmailStr


class CompleteUserOnboardingSchema(BaseModel):
    name: str
    first_surname: str
    second_surname: Optional[str] = None


class UpdateUserSchema(BaseModel):
    role_id: Optional[int] = None
    name: Optional[str] = None
    first_surname: Optional[str] = None
    second_surname: Optional[str] = None
    email: Optional[EmailStr] = None


class UpdateCurrentUserSchema(BaseModel):
    name: Optional[str] = None
    first_surname: Optional[str] = None
    second_surname: Optional[str] = None
    email: Optional[EmailStr] = None


class UpdatePasswordSchema(BaseModel):
    old_password: str
    new_password: str
    repeat_password: str
