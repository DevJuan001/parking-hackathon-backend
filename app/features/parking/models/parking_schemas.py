from pydantic import BaseModel

from app.utils.safe_types import safe_str


class CreatePlateSchema(BaseModel):
    plate: str = safe_str(min_length=6, max_length=6)


class FindPlateSchema(BaseModel):
    plate: str = safe_str(min_length=6, max_length=6)
