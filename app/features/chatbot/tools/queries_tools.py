from app.utils.logger import get_logger
from app.features.chatbot.services.chatbot_service import ChatbotService

logger = get_logger("chatbot.tools.queries")


def tool_get_occupancy_stats(parking_id: int) -> dict:
    error, data = ChatbotService.get_occupancy_stats(parking_id)

    if error:
        return {"error": error}

    return {"success": True, "data": data}


def tool_get_daily_summary(parking_id: int) -> dict:
    error, data = ChatbotService.get_daily_summary(parking_id)

    if error:
        return {"error": error}

    return {"success": True, "data": data}
