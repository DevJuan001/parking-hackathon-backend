from app.utils.logger import get_logger
from app.core.exception import ServiceError
from app.core.database import get_connection
from app.features.reservations.models.reservations_schema import FilterReservationsSchema
from app.features.reservations.repositories.reservations_repository import ReservationsRepository


logger = get_logger("reservations.service")


class ReservationsService():
    @staticmethod
    def get_all_reservations(filters: FilterReservationsSchema, parking_id: int):
        connection = get_connection()

        try:
            error, reservations = ReservationsRepository.find_all_reservations(
                filters, parking_id, connection
            )

            if error:
                raise ServiceError(error)

            return None, reservations

        except ServiceError as e:
            return e.message, None

        except Exception as e:
            logger.error(
                "Error en get_all_reservations: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener las reservas", None

        finally:
            connection.close()
