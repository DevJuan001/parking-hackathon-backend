from pydantic import BaseModel


class ChatbotResponse(BaseModel):
    response: str
    actions: list[dict] | None = None
    sources: list[str] | None = None
