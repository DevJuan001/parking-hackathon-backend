import json

from app.core.redis import get_redis
from app.utils.logger import get_logger

logger = get_logger("chatbot.conversation_service")


class ConversationService:

    HISTORY_PREFIX = "chatbot:history:"
    TTL = 86400
    MAX_MESSAGES = 40

    @staticmethod
    def key(parking_id: int, user_id: int) -> str:
        return f"{ConversationService.HISTORY_PREFIX}{parking_id}:{user_id}"

    @staticmethod
    async def get_history(parking_id: int, user_id: int, limit: int = 15) -> list:
        redis = await get_redis()

        key = ConversationService.key(parking_id, user_id)

        try:
            raw = await redis.lrange(key, -limit, -1)
            messages = [json.loads(m) for m in raw]

        except Exception as e:
            logger.error(
                "Error al obtener el historial de chat: %s",
                e,
                exc_info=True
            )
            return []

        # Sacamos secuencias incompletas del final (tool o tool_calls sin respuesta colgando)
        while messages:
            last = messages[-1]

            if last.get("role") == "tool" or (last.get("role") == "assistant" and "tool_calls" in last):
                messages.pop()

            else:
                break

        # Sacamos tool messages huérfanos del medio:
        # un tool solo se conserva si su tool_call_id matchea algún id de tool_calls del assistant inmediatamente anterior.
        valid_ids: set[str] = set()
        clean: list[dict] = []

        for msg in messages:
            role = msg.get("role", "")

            if role == "assistant" and "tool_calls" in msg:
                valid_ids.clear()

                for tc in msg["tool_calls"]:
                    valid_ids.add(tc.get("id", ""))

                clean.append(msg)

            elif role == "tool" and msg.get("tool_call_id") in valid_ids:
                clean.append(msg)

            elif role in ("user", "assistant"):
                valid_ids.clear()
                clean.append(msg)
            # tool sin assistant previo → descartado silenciosamente

        return clean

    @staticmethod
    async def add_message(
        parking_id: int,
        user_id: int,
        role: str,
        content: str,
        tool_calls: list = None,
        tool_call_id: str = None,
    ) -> None:
        redis = await get_redis()

        key = ConversationService.key(parking_id, user_id)

        message = {
            "role": role,
            "content": content
        }

        if tool_calls:
            message["tool_calls"] = tool_calls

        if tool_call_id:
            message["tool_call_id"] = tool_call_id

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
