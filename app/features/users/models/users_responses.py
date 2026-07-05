from pydantic import BaseModel, EmailStr

from app.utils.base_schema import BaseSchema


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
    name: str
    first_surname: str
    second_surname: str
    email: EmailStr
    created_at: str
    status: int


class UserStatsResponse(BaseModel):
    total: int
    active: int
    disabled: int
    created_this_week: int


class SurnameResponse(BaseModel):
    surname: str
