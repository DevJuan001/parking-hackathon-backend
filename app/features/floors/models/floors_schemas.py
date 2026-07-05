from typing import Optional
from pydantic import BaseModel

from app.utils.safe_types import safe_optional_str, safe_str


class CreateFloorSchema(BaseModel):
    name: str = safe_str(min_length=1, max_length=100)


class UpdateFloorSchema(BaseModel):
    name: Optional[str] = safe_optional_str(min_length=1, max_length=100)
