from pydantic import BaseModel


class CountryResponse(BaseModel):
    id: int
    name: str
    iso_code: str
