from app.core.database import get_connection
from app.utils.logger import get_logger
from app.features.chatbot.repositories.chatbot_repository import ChatbotRepository

logger = get_logger("chatbot.service")


class ChatbotService:

    @staticmethod
    def get_occupancy_stats(parking_id: int):
        connection = get_connection()

        try:
            error, data = ChatbotRepository.get_occupancy_stats(
                parking_id, connection
            )

            if error:
                return error, None

            return None, data

        except Exception as e:
            logger.error("Error en get_occupancy_stats: %s", e, exc_info=True)
            return "Error al intentar obtener las estadísticas", None

        finally:
            connection.close()

    @staticmethod
    def get_daily_summary(parking_id: int):
        connection = get_connection()

        try:
            error, data = ChatbotRepository.get_daily_summary(
                parking_id, connection
            )

            if error:
                return error, None

            return None, data

        except Exception as e:
            logger.error("Error en get_daily_summary: %s", e, exc_info=True)
            return "Error al intentar obtener el resumen del día", None

        finally:
            connection.close()

    @staticmethod
    def get_parking_info(parking_id: int):
        connection = get_connection()

        try:
            error, data = ChatbotRepository.get_parking_info(
                parking_id, connection
            )

            if error:
                return error, None

            if not data:
                return "No se encontró información del parking", None

            return None, data

        except Exception as e:
            logger.error("Error en get_parking_info: %s", e, exc_info=True)
            return "Error al intentar obtener la información del parking", None

        finally:
            connection.close()
