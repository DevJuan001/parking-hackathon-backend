from pydantic import BaseModel


class ChatbotResponse(BaseModel):
    response: str
    actions: list[dict] | None = None
    sources: list[str] | None = None


class KnowledgeDocumentResponse(BaseModel):
    id: str
    source: str
    category: str
    parking_id: int
    created_at: str
