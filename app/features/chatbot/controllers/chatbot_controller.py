from app.features.chatbot.models.chatbot_schemas import ChatbotAskSchema
from app.features.chatbot.services.rag_service import RAGService
from app.middlewares.jwt_middleware import AuthPayload


class ChatbotController:

    @staticmethod
    async def ask(query: ChatbotAskSchema, payload: AuthPayload) -> dict:
        result = await RAGService.ask(query.message, payload)

        return {
            "data": result
        }
