from datetime import date, datetime, time

from pydantic import EmailStr

from app.utils.logger import get_logger
from app.core.exception import ServiceError
from app.core.database import get_connection
from app.utils.round_to_50 import round_up_to_next_50
from app.utils.plate_formatter import plate_formatter
from app.features.tariffs.repositories.tariffs_repository import TariffsRepository
from app.features.parking.repositories.parkings_repository import ParkingsRepository
from app.features.reservations.repositories.reservations_repository import ReservationsRepository
from app.tasks.email_tasks import send_reservation_created_email, send_reservation_cancelled_email
from app.features.reservations.models.reservations_schemas import FilterReservationsSchema, UpdateReservationSchema


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
        name: str,
        plate: str,
        email: EmailStr,
        level: int,
        start_date,
        start_time,
        end_date=None,
        end_time=None,
    ):
        connection = get_connection()

        try:
            # Juntamos la fecha y la hora de inicio
            start_datetime = datetime.combine(start_date, start_time)

            if end_date is not None:
                effective_end_time = end_time if end_time is not None else time(
                    23, 59, 59
                )
                end_datetime = datetime.combine(end_date, effective_end_time)
            else:
                end_datetime = None

            # Validamos que la fecha de fin no sea mayor a la de inicio
            if end_date is not None and start_date > end_date:
                raise ServiceError(
                    "La fecha de fin debe ser igual o posterior a la fecha de inicio"
                )

            today = date.today()

            if start_date < today:
                raise ServiceError(
                    "No se puede crear una reserva en una fecha anterior a la actual"
                )

            error, success, message, reservation_id = ReservationsRepository.create_reservation(
                parking_id=parking_id,
                name=name,
                email=email,
                plate=plate,
                level=level,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                connection=connection,
            )

            if error or not success:
                raise ServiceError(error or message)

            # Buscamos la información del parking mediante el id
            error, parking = ParkingsRepository.find_parking_by_id(
                parking_id, connection
            )

            if error:
                raise ServiceError(error)

            # Formateamos la placa
            plate_text = plate_formatter(plate)

            if not plate_text:
                raise ServiceError("La placa no puede estar vacía")

            if plate_text[-1].isalpha():
                vehicle_type = 2
            else:
                vehicle_type = 1

            total_time = start_datetime - end_datetime if end_datetime else 0

            error, rate = TariffsRepository.find_rate_by_vehicle_type(
                parking_id, vehicle_type, connection
            )

            if error or not rate:
                raise ServiceError(error or "Tarifa no encontrada")

            # Redondeamos el valor total a pagar
            total_raw = round(total_time * rate.value, 2)
            total = round_up_to_next_50(total_raw)

            connection.commit()

            send_reservation_created_email.delay(
                user_email=email,
                user_name=name,
                parking_name=parking.name,
                parking_location=parking.country,
                reservation_id=reservation_id,
                reservation_name=name,
                total=total if total else rate.value * 2,
                payment_status="Pagado",
                start_date=start_date,
                start_time=start_time,
                end_date=end_date if end_date else None,
                end_time=end_datetime if end_datetime else None,
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

    @staticmethod
    def update_reservation(reservation_id: int, reservation_data: UpdateReservationSchema, parking_id: int):
        connection = get_connection()

        try:
            error, existing_reservation = ReservationsRepository.find_reservation_by_id(
                reservation_id, parking_id, connection
            )

            if error or not existing_reservation:
                raise ServiceError(error or "Reserva no encontrada")

            today = date.today()
            start_date = datetime.combine(
                reservation_data.start_date or existing_reservation.start_date,
                reservation_data.start_time or existing_reservation.start_time
            )

            if reservation_data.end_date is not None or existing_reservation.end_date is not None:
                end_date = datetime.combine(
                    reservation_data.end_date or existing_reservation.end_date,
                    reservation_data.end_time or existing_reservation.end_time
                )
            else:
                end_date = None

            if start_date.date() < today:
                raise ServiceError(
                    "No se puede editar la reserva de una fecha anterior a la actual"
                )

            reservation_data.start_date = start_date
            reservation_data.end_date = end_date

            error, success, message = ReservationsRepository.update_reservation(
                reservation_id, parking_id, reservation_data, connection
            )

            if error or not success:
                raise ServiceError(
                    error or "Error al intentar actualizar la reserva"
                )

            connection.commit()

            if (reservation_data.status == 1):
                send_reservation_cancelled_email.delay(
                    user_email=existing_reservation.email,
                    user_name=existing_reservation.name,
                    reservation_id=reservation_id,
                    reservation_name=existing_reservation.name,
                    template_name="reservation_cancelled_by_admin.html",
                    start_date=existing_reservation.start_date,
                    start_time=existing_reservation.start_time,
                    end_date=existing_reservation.end_date if existing_reservation.end_date else None,
                    end_time=existing_reservation.end_time if existing_reservation.end_time else None,
                )

            return None, True, "Reserva actualizada correctamente"

        except ServiceError as e:
            connection.rollback()
            return e.message, False, None

        except Exception as e:
            connection.rollback()
            logger.error(
                "Error en update_reservation_status: %s",
                e,
                exc_info=True
            )
            return "Error al intentar actualizar el estado de la reserva", False, None

        finally:
            connection.close()

    @staticmethod
    def delete_reservation(reservation_id: int, parking_id: int):
        connection = get_connection()

        try:
            error, existing = ReservationsRepository.find_reservation_by_id(
                reservation_id, parking_id, connection
            )

            if error or not existing:
                raise ServiceError("Reserva no encontrada")

            if existing.status == 3:
                raise ServiceError(
                    "No se puede eliminar una reserva que está en proceso"
                )

            error, success, message = ReservationsRepository.delete_reservation(
                reservation_id, parking_id, connection
            )

            if error or not success:
                raise ServiceError(
                    error or "Error al intentar eliminar la reserva"
                )

            connection.commit()

            if (existing.status not in (1, 4)):
                send_reservation_cancelled_email.delay(
                    user_email=existing.email,
                    user_name=existing.name,
                    reservation_id=reservation_id,
                    reservation_name=existing.name,
                    template_name="reservation_cancelled_by_admin.html",
                    start_date=existing.start_date,
                    start_time=existing.start_time,
                    end_date=existing.end_date if existing.end_date else None,
                    end_time=existing.end_time if existing.end_time else None,
                )

            return None, True, "Reserva eliminada correctamente"

        except ServiceError as e:
            connection.rollback()
            return e.message, False, None

        except Exception as e:
            connection.rollback()
            logger.error(
                "Error en delete_reservation: %s",
                e,
                exc_info=True
            )
            return "Error al intentar eliminar la reserva", False, None

        finally:
            connection.close()
