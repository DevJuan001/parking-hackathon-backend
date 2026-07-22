from fastapi import HTTPException

from app.features.chatbot.models.chatbot_schemas import ChatbotAskSchema
from app.features.chatbot.services.rag_service import RAGService
from app.features.chatbot.services.chatbot_service import ChatbotService
from app.tasks.knowledge_tasks import rebuild_parking_knowledge


class ChatbotController:

    @staticmethod
    async def ask(query: ChatbotAskSchema, payload: dict) -> dict:
        result = await RAGService.ask(query.message, payload)

        return {
            "data": result
        }

    @staticmethod
    def get_knowledge_sources(payload: dict) -> dict:
        parking_id = int(payload["parking_id"])

        error, sources = ChatbotService.get_knowledge_sources(parking_id)

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "data": sources or []
        }

    @staticmethod
    def delete_knowledge_source(source: str, payload: dict) -> dict:
        parking_id = int(payload["parking_id"])

        error, success = ChatbotService.delete_knowledge_source(
            parking_id, source)

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "success": True,
            "message": f"Fuente '{source}' eliminada correctamente"
        }

    @staticmethod
    def reindex_knowledge(payload: dict) -> dict:
        parking_id = int(payload["parking_id"])

        rebuild_parking_knowledge.delay(parking_id)

        return {
            "success": True,
            "message": "Reindexación iniciada. El conocimiento se actualizará en segundo plano.",
        }

    @staticmethod
    def get_knowledge_chunks(payload: dict) -> dict:
        parking_id = int(payload["parking_id"])

        error, chunks = ChatbotService.get_knowledge_chunks(parking_id)

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "data": chunks or []
        }
