from pydantic import BaseModel


class CreatePlateSchema(BaseModel):
    plate: str


class FindPlateSchema(BaseModel):
    plate: str