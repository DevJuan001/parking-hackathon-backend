from app.core.database import get_connection
from app.utils.logger import get_logger
from app.features.chatbot.repositories.chatbot_repository import ChatbotRepository

logger = get_logger("chatbot.context_builder")


class ContextBuilder:

    @staticmethod
    def build_snapshot(parking_id: int, role: str = "Admin") -> str:
        connection = get_connection()

        if not connection:
            return "No se pudo establecer conexión con la base de datos."

        try:
            error, data = ChatbotRepository.get_snapshot_data(
                parking_id, connection
            )

            if error:
                return "No se pudo consultar el estado del estacionamiento."

            parts = []

            if data.get("parking_name"):
                parts.append(f"Estacionamiento: {data['parking_name']}")

            if data.get("total_floors") is not None:
                parts.append(f"Total de pisos: {data['total_floors']}")

            if data.get("total_spots") is not None:
                parts.append(f"Total de plazas: {data['total_spots']}")

            if data.get("occupied_spots") is not None:
                parts.append(f"Plazas ocupadas: {data['occupied_spots']}")

            if data.get("active_entries") is not None:
                parts.append(f"Ingresos activos: {data['active_entries']}")

            # Pagos de hoy
            if role == "Admin" and data.get("today_payments"):
                count, total = data["today_payments"]
                parts.append(f"Pagos de hoy: {count} — Total: ${total:.2f}")

            if not parts:
                return "No se encontró información para este estacionamiento."

            return " | ".join(parts)

        except Exception as e:
            logger.error(
                "Error al construir el snapshot del parking: %s",
                e,
                exc_info=True
            )
            return "No se pudo obtener el estado actual del estacionamiento."

        finally:
            connection.close()
