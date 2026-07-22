from app.utils.logger import get_logger
from app.core.database import get_connection
from app.features.chatbot.repositories.chatbot_repository import ChatbotRepository
from app.features.chatbot.repositories.vector_repository import VectorRepository

logger = get_logger("chatbot.knowledge_generator")


class KnowledgeGenerator:

    @staticmethod
    def generate_all(parking_id: int) -> tuple[str | None, bool]:
        connection = get_connection()

        try:
            error, parking = ChatbotRepository.get_parking_info(
                parking_id, connection
            )

            if error:
                return error, False

            if not parking:
                return "No se encontró el parking", False

            error, tariffs = ChatbotRepository.get_tariffs_with_vehicle_type(
                parking_id, connection
            )

            if error:
                return error, False

            error, payment_methods = ChatbotRepository.get_all_payment_methods(
                connection
            )

            if error:
                return error, False

            chunks = []

            chunks.append({
                "id": f"parking_{parking_id}_parking_info_0",
                "text": (
                    f"El parking se llama {parking['name']}. "
                    f"Está ubicado en {parking['address']}. "
                    f"Teléfono de contacto: {parking['phone']}."
                ),
                "source": "parking_info",
                "category": "informacion_general",
                "chunk_index": 0,
            })

            for index, tariff in enumerate(tariffs or []):
                chunks.append({
                    "id": f"parking_{parking_id}_tarifas_{index}",
                    "text": (
                        f"Tarifa para {tariff['vehicle_type']}: "
                        f"${float(tariff['value']):.2f}/hora"
                    ),
                    "source": "tarifas",
                    "category": "tarifas",
                    "chunk_index": index,
                })

            if payment_methods:
                methods_str = ", ".join(
                    pm["name"] for pm in payment_methods
                )
                chunks.append({
                    "id": f"parking_{parking_id}_metodos_pago_0",
                    "text": (
                        f"Métodos de pago disponibles: {methods_str}."
                    ),
                    "source": "metodos_pago",
                    "category": "pagos",
                    "chunk_index": 0,
                })

            delete_error, _ = VectorRepository.delete_all_by_parking(
                parking_id
            )

            if delete_error:
                return delete_error, False

            upsert_error, _ = VectorRepository.upsert_chunks(
                parking_id, chunks
            )

            if upsert_error:
                return upsert_error, False

            logger.info(
                "Conocimiento regenerado para parking %d: %d chunks",
                parking_id,
                len(chunks),
            )

            return None, True

        except Exception as e:
            logger.error(
                "Error al generar conocimiento para parking %d: %s",
                parking_id,
                e,
                exc_info=True,
            )
            return f"Error al generar el conocimiento: {str(e)}", False

        finally:
            connection.close()
