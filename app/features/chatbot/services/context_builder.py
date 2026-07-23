import json

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
            else:
                logger.warning(
                    "parking_name vacío o nulo para parking_id=%s", parking_id
                )

            if data.get("total_floors") is not None:
                parts.append(f"Total de pisos: {data['total_floors']}")

            if data.get("total_spots") is not None:
                parts.append(f"Total de plazas: {data['total_spots']}")

            if data.get("occupied_spots") is not None:
                parts.append(f"Plazas ocupadas: {data['occupied_spots']}")

            if data.get("active_entries") is not None:
                parts.append(f"Ingresos activos: {data['active_entries']}")

            if data.get("tariffs"):
                tariff_parts = []

                for vehicle_type, value in data["tariffs"]:
                    tariff_parts.append(f"{vehicle_type}: ${value:.2f}")

                parts.append("Tarifas: " + " | ".join(tariff_parts))

            # Plazas por piso (snapshot rico)
            if data.get("floors_with_spots"):
                total_spots = data.get("total_spots") or 0

                if total_spots > 100:
                    parts.append(
                        "Plazas por piso: [más de 100, consultá list_spots para verlas]"
                    )

                else:
                    floor_lines = []

                    for floor_name, spots_json in data["floors_with_spots"]:
                        spots = json.loads(spots_json) if isinstance(
                            spots_json, str
                        ) else spots_json

                        spots_str = ", ".join(str(s) for s in spots)

                        floor_lines.append(f"{floor_name}: {spots_str}")

                    parts.append("Plazas: " + " | ".join(floor_lines))

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
