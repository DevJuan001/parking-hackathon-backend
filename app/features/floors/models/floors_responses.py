from pydantic import BaseModel


class FloorResponse(BaseModel):
    id: int
    name: str
    created_at: str
