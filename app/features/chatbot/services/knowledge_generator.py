from app.core.database import get_connection
from app.features.chatbot.repositories.vector_repository import VectorRepository
from app.features.parking.repositories.vehicle_types_repository import (
    VehicleTypesRepository,
)
from app.features.parking.services.parking_service import ParkingService
from app.features.payments.repositories.payments_repository import PaymentsRepository
from app.features.tariffs.repositories.tariffs_repository import TariffsRepository
from app.utils.logger import get_logger

logger = get_logger("chatbot.knowledge_generator")


class KnowledgeGenerator:

    @staticmethod
    def generate_all(parking_id: str) -> tuple[str | None, bool]:
        connection = get_connection()

        try:
            error, parking = ParkingService.get_parking_by_private_info(
                parking_id)

            if error or not parking:
                return error or "No se encontró el parking", False

            error, tariffs = TariffsRepository.find_all_tariffs(
                parking_id, connection
            )

            if error:
                return error, False

            error, vehicle_types = VehicleTypesRepository.find_all_vehicle_types(
                connection
            )

            if error:
                return error, False

            vehicle_type_by_id = {
                vehicle_type.id: vehicle_type.name
                for vehicle_type in vehicle_types
            }

            error, payment_methods = PaymentsRepository.find_all_payment_methods(
                connection
            )

            if error:
                return error, False

            chunks = []

            chunks.append({
                "id": f"parking_{parking_id}_parking_info_0",
                "text": (
                    f"El parking se llama {parking.name}. "
                    f"Dirección: {parking.address}."
                ),
                "source": "parking_info",
                "category": "informacion_general",
                "chunk_index": 0,
            })

            for index, tariff in enumerate(tariffs or []):
                name = vehicle_type_by_id.get(
                    tariff.vehicle_type,
                    str(tariff.vehicle_type)
                )

                chunks.append({
                    "id": f"parking_{parking_id}_tarifas_{index}",
                    "text": (
                        f"Tarifa para {name}: "
                        f"${float(tariff.value):.2f}/hora"
                    ),
                    "source": "tarifas",
                    "category": "tarifas",
                    "chunk_index": index,
                })

            if payment_methods:
                methods_str = ", ".join(
                    payment.name for payment in payment_methods)

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
                "Conocimiento regenerado para parking %s: %d chunks",
                parking_id,
                len(chunks),
            )

            return None, True

        except Exception as e:
            logger.exception(
                "Error al generar conocimiento para parking %s",
                parking_id,
            )
            return f"Error al generar el conocimiento: {e!s}", False

        finally:
            connection.close()
