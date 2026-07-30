from app.utils.logger import get_logger
from app.core.exception import ServiceError
from app.core.database import get_connection
from app.features.reservations.models.reservations_schema import FilterReservationsSchema
from app.features.reservations.repositories.reservations_repository import ReservationsRepository
from app.features.users.repositories.users_repository import UsersRepository
from app.tasks.email_tasks import send_reservation_created_email


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

    @staticmethod
    def create_reservation(
        parking_id: int,
        user_id: int,
        name: str,
        level: int,
        start_date,
        end_date,
    ):
        connection = get_connection()

        try:
            error, user = UsersRepository.find_user_by_id(
                parking_id, user_id, connection
            )

            if error or not user:
                raise ServiceError(error or "Usuario no encontrado")

            if user.role != "Cliente":
                raise ServiceError("El usuario target debe tener rol Cliente")

            error, success, message = ReservationsRepository.create_reservation(
                parking_id=parking_id,
                user_id=user_id,
                name=name,
                level=level,
                start_date=start_date,
                end_date=end_date,
                connection=connection,
            )

            if error or not success:
                raise ServiceError(error or message)

            connection.commit()

            send_reservation_created_email.delay(
                user_email=user.email,
                user_name=user.name,
                reservation_name=name,
                level=level,
                start_date=str(start_date),
                end_date=str(end_date),
            )

            return None, True, "Reserva creada correctamente"

        except ServiceError as e:
            connection.rollback()
            return e.message, False, None

        except Exception as e:
            connection.rollback()
            logger.error(
                "Error en create_reservation: %s",
                e,
                exc_info=True
            )
            return "Error al intentar crear la reserva", False, None

        finally:
            connection.close()
