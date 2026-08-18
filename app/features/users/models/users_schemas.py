from datetime import date

from pydantic import BaseModel, EmailStr, Field

from app.utils.safe_types import safe_optional_str, safe_str


class UsersFiltersSchema(BaseModel):
    role_order: int | None = None
    first_surname: str | None = safe_optional_str(
        min_length=1, max_length=256
    )
    name_order: str | None = safe_optional_str(
        min_length=1, max_length=256
    )
    start_date: date | None = None
    end_date: date | None = None
    page: int = Field(1, ge=1)
    per_page: int = Field(15, ge=1, le=100)


class CreateUserSchema(BaseModel):
    role_id: int
    name: str | None = safe_optional_str(max_length=128)
    first_surname: str | None = safe_optional_str(max_length=128)
    second_surname: str | None = safe_optional_str(max_length=128)
    email: EmailStr = safe_str(max_length=254)


class CompleteUserOnboardingSchema(BaseModel):
    name: str = safe_str(min_length=1, max_length=128)
    first_surname: str = safe_str(min_length=1, max_length=128)
    second_surname: str | None = safe_optional_str(
        min_length=1, max_length=256
    )


class UpdateUserSchema(BaseModel):
    role_id: int | None = None
    name: str | None = safe_optional_str(
        min_length=1, max_length=256
    )
    first_surname: str | None = safe_optional_str(
        min_length=1, max_length=256
    )
    second_surname: str | None = safe_optional_str(
        min_length=1, max_length=256
    )
    email: EmailStr | None = safe_optional_str(
        max_length=256
    )


class UpdateCurrentUserSchema(BaseModel):
    name: str | None = safe_optional_str(
        min_length=1, max_length=256
    )
    first_surname: str | None = safe_optional_str(
        min_length=1, max_length=256
    )
    second_surname: str | None = safe_optional_str(
        min_length=1, max_length=256
    )
    email: EmailStr | None = safe_optional_str(
        max_length=256
    )


class UpdatePasswordSchema(BaseModel):
    old_password: str = safe_str(min_length=8, max_length=128)
    new_password: str = safe_str(min_length=8, max_length=128)
    repeat_password: str = safe_str(min_length=8, max_length=128)
