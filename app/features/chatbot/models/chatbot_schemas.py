from pydantic import BaseModel
from app.utils.safe_types import safe_str


class ChatbotAskSchema(BaseModel):
    message: str = safe_str(min_length=1, max_length=2000)
