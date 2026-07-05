from pydantic import BaseModel, Field


class FloorsFiltersSchema(BaseModel):
    pass


class CreateFloorSchema(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class UpdateFloorSchema(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
