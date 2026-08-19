from datetime import UTC, datetime

from app.core.database import get_connection
from app.features.entries.repositories.entries_repository import EntriesRepository
from app.features.exits.models.exits_schemas import StatsExitsFiltersSchema
from app.features.exits.repositories.exits_repository import ExitsRepository
from app.features.parking.services.parking_service import ParkingService
from app.features.payments.repositories.payments_repository import PaymentsRepository
from app.features.spots.services.spots_service import SpotsService
from app.utils.logger import get_logger

logger = get_logger("chatbot.service")


class ChatbotService:

    @staticmethod
    def get_parking_info(parking_id: str):
        return ParkingService.get_parking_by_id(parking_id)

    @staticmethod
    def get_occupancy_stats(parking_id: str):
        return SpotsService.get_occupancy_stats(parking_id)

    @staticmethod
    def get_daily_summary(parking_id: str):
        connection = get_connection()

        try:
            error, entries = EntriesRepository.count_entry_stats(
                parking_id, connection
            )

            if error:
                return error, None

            error, exits = ExitsRepository.count_exit_stats(
                StatsExitsFiltersSchema(), parking_id, connection
            )

            if error:
                return error, None

            error, payments = PaymentsRepository.sum_payment_stats(
                parking_id, connection
            )

            if error:
                return error, None

            return None, {
                "date": datetime.now(UTC).date().isoformat(),
                "entries_today": entries.today,
                "exits_today": exits["today"],
                "revenue_today": payments["today"],
            }

        except Exception:
            logger.exception("Error en get_daily_summary")
            return "Error al intentar obtener el resumen del día", None

        finally:
            connection.close()