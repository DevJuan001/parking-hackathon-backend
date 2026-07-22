import json

from app.core.redis import get_redis
from app.utils.logger import get_logger

logger = get_logger("chatbot.conversation_service")


class ConversationService:

    HISTORY_PREFIX = "chatbot:history:"
    TTL = 86400
    MAX_MESSAGES = 20

    @staticmethod
    def key(parking_id: int, user_id: int) -> str:
        return f"{ConversationService.HISTORY_PREFIX}{parking_id}:{user_id}"

    @staticmethod
    async def get_history(parking_id: int, user_id: int, limit: int = 10) -> list:
        redis = await get_redis()

        key = ConversationService.key(parking_id, user_id)

        try:
            messages = await redis.lrange(key, -limit, -1)

            return [json.loads(m) for m in messages]

        except Exception as e:
            logger.error(
                "Error al obtener el historial de chat: %s",
                e,
                exc_info=True
            )
            return []

    @staticmethod
    async def add_message(
        parking_id: int,
        user_id: int,
        role: str,
        content: str,
        tool_calls: list = None,
    ) -> None:
        redis = await get_redis()

        key = ConversationService.key(parking_id, user_id)

        message = {
            "role": role,
            "content": content
        }

        if tool_calls:
            message["tool_calls"] = tool_calls

        try:
            await redis.rpush(key, json.dumps(message))

            await redis.ltrim(key, -ConversationService.MAX_MESSAGES, -1)

            await redis.expire(key, ConversationService.TTL)

        except Exception as e:
            logger.error(
                "Error al agregar mensaje al historial: %s",
                e,
                exc_info=True
            )

    @staticmethod
    async def clear_history(parking_id: int, user_id: int) -> None:
        redis = await get_redis()

        key = ConversationService.key(parking_id, user_id)

        try:
            await redis.delete(key)

        except Exception as e:
            logger.error(
                "Error al limpiar el historial de chat: %s",
                e,
                exc_info=True
            )
