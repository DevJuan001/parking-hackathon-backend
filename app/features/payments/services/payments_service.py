from datetime import datetime
from app.utils.logger import get_logger
from app.core.exception import ServiceError
from app.core.database import get_connection
from app.utils.date_formatter import date_formatter
from app.utils.plate_formatter import plate_formatter
from app.utils.round_to_50 import round_up_to_next_50
from app.features.exits.repositories.exits_repository import ExitsRepository
from app.features.parking.repositories.plates_repository import PlatesRepository
from app.features.tariffs.repositories.tariffs_repository import TariffsRepository
from app.features.entries.repositories.entries_repository import EntriesRepository
from app.features.spots.repositories.spots_repository import SpotsRepository
from app.features.payments.models.payments_responses import CalculatePaymentResponse
from app.features.payments.repositories.payments_repository import PaymentsRepository
from app.features.payments.models.payments_schemas import CreatePaymentSchema, PaymentsFiltersSchema

logger = get_logger("payments.service")


class PaymentsService:

    @staticmethod
    def get_all_payments(parking_id: int, filters: PaymentsFiltersSchema):
        connection = get_connection()

        try:
            error, payments = PaymentsRepository.find_all_payments(
                parking_id, connection
            )

            if error:
                raise ServiceError(error)

            return None, payments

        except ServiceError as e:
            return e.message, None

        except Exception as e:
            logger.error(
                "Error en get_all_payments: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener los pagos", None

        finally:
            connection.close()

    @staticmethod
    def get_payment_by_id(parking_id: int, payment_id: int):
        connection = get_connection()

        try:
            error, payment = PaymentsRepository.find_payment_by_id(
                parking_id, payment_id, connection
            )

            if error or not payment:
                raise ServiceError(error)

            return None, payment

        except ServiceError as e:
            return e.message, None

        except Exception as e:
            logger.error(
                "Error en get_payment_by_id: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener el pago", None

        finally:
            connection.close()

    @staticmethod
    def get_payments_by_plate(parking_id: int, plate_id: int):
        connection = get_connection()

        try:
            error, payments = PaymentsRepository.find_payments_by_plate(
                parking_id, plate_id, connection
            )

            if error:
                raise ServiceError(error)

            return None, payments

        except ServiceError as e:
            return e.message, None

        except Exception as e:
            logger.error(
                "Error en get_payments_by_plate: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener los pagos de la placa", None

        finally:
            connection.close()

    @staticmethod
    def get_payments_growth(parking_id: int, period: str):
        connection = get_connection()

        try:
            error, exits = PaymentsRepository.find_payments_growth(
                parking_id, period, connection
            )

            if error:
                raise ServiceError(error)

            return None, exits

        except ServiceError as e:
            return e.message, None

        except Exception as e:
            logger.error(
                "Error en get_payments_growth: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener el crecimiento de los pagos", None

        finally:
            connection.close()

    @staticmethod
    def get_all_payment_methods():
        connection = get_connection()

        try:
            error, methods = PaymentsRepository.find_all_payment_methods(
                connection
            )

            if error:
                raise ServiceError(error)

            return None, methods

        except ServiceError as e:
            return e.message, None

        except Exception as e:
            logger.error(
                "Error en get_all_payment_methods: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener los metodos de pago", None

        finally:
            connection.close()

    @staticmethod
    def calculate_payment(parking_id: int, plate: str):
        connection = get_connection()

        try:
            plate_text = plate_formatter(plate)

            error, plate_data = PlatesRepository.get_plate_by_name(
                parking_id, plate_text, connection
            )

            if error or not plate_data:
                raise ServiceError(
                    error or "No se encontro esta placa, revisa que este escrita correctamente e intentalo de nuevo"
                )

            plate_id = plate_data[0].id
            vehicle_type = plate_data[0].vehicle_type

            error, entry = EntriesRepository.find_latest_entry(
                parking_id, plate_id, connection
            )

            if error or not entry:
                raise ServiceError(
                    error or "No se encontró un ingreso para esta placa"
                )

            entry_time = entry.created_at

            error, latest_exit = ExitsRepository.find_latest_exit(
                parking_id, plate_id, connection
            )

            if error:
                raise ServiceError(error)

            if latest_exit and latest_exit.created_at >= entry_time:
                raise ServiceError(
                    "El vehiculo ya tiene una salida registrada"
                )

            exit_time = datetime.now()

            if exit_time <= entry_time:
                raise ServiceError(
                    "La hora actual es anterior a la hora de ingreso"
                )

            diff = exit_time - entry_time

            hours_parked = round(diff.total_seconds() / 3600, 2)

            error, rate = TariffsRepository.find_rate_by_vehicle_type(
                parking_id, vehicle_type, connection
            )

            if error or not rate:
                raise ServiceError(error or "Tarifa no encontrada")

            rate_value = rate.value

            total_raw = round(hours_parked * rate_value, 2)
            total = round_up_to_next_50(total_raw)

            return None, CalculatePaymentResponse(
                plate=plate_data[0].plate,
                entry_time=entry_time,
                exit_time=exit_time,
                hours_parked=hours_parked,
                rate_value=rate_value,
                total=total
            )

        except ServiceError as e:
            return e.message, None

        except Exception as e:
            logger.error(
                "Error en calculate_payment: %s",
                e,
                exc_info=True
            )
            return "Error al calcular el pago", None

        finally:
            connection.close()

    @staticmethod
    async def create_payment(parking_id: int, payment_data: CreatePaymentSchema):
        connection = get_connection()

        try:
            plate_text = plate_formatter(payment_data.plate)

            error, plate_list = PlatesRepository.get_plate_by_name(
                parking_id, plate_text, connection
            )

            if error or not plate_list:
                raise ServiceError(error or "Placa no encontrada")

            plate_id = plate_list[0].id
            vehicle_type = plate_list[0].vehicle_type

            error, entry = EntriesRepository.find_latest_entry(
                parking_id, plate_id, connection
            )

            if error or not entry:
                raise ServiceError(
                    error or "No se encontró un ingreso para esta placa"
                )

            entry_time = entry.created_at

            error, latest_exit = ExitsRepository.find_latest_exit(
                parking_id, plate_id, connection
            )

            if error:
                raise ServiceError(error)

            if latest_exit and latest_exit.created_at >= entry_time:
                raise ServiceError(
                    "El vehiculo ya tiene una salida registrada"
                )

            exit_time = payment_data.exit_time

            if exit_time <= entry_time:
                raise ServiceError(
                    "La hora de salida debe ser posterior a la hora de ingreso"
                )

            diff = exit_time - entry_time

            hours_parked = round(diff.total_seconds() / 3600, 2)

            error, rate = TariffsRepository.find_rate_by_vehicle_type(
                parking_id, vehicle_type, connection
            )

            if error or not rate:
                raise ServiceError(error or "Tarifa no encontrada")

            value_raw = round(hours_parked * rate.value, 2)

            if value_raw < 0:
                raise ServiceError(
                    "El valor calculado del pago es invalido"
                )

            value = round_up_to_next_50(value_raw)

            error, success, message = ExitsRepository.create_exit(
                parking_id=parking_id,
                plate_id=plate_id,
                connection=connection
            )

            if error or not success:
                raise ServiceError(
                    error or "Error al intentar crear la salida"
                )

            error, success, message = PaymentsRepository.create_payment(
                parking_id=parking_id,
                plate_id=plate_id,
                spot_id=entry.spot_id,
                value=value,
                payment_method_id=payment_data.payment_method,
                connection=connection
            )

            if error or not success:
                raise ServiceError(error)

            if entry.spot_id is not None:
                error, success, message = SpotsRepository.update_spot_status(
                    parking_id, entry.spot_id, 2, connection
                )

                if error or not success:
                    raise ServiceError(
                        error or "Error al liberar la plaza"
                    )

            connection.commit()

            return None, True, "Pago registrado correctamente"

        except ServiceError as e:
            connection.rollback()
            return e.message, False, None

        except Exception as e:
            connection.rollback()
            logger.error(
                "Error en create_payment: %s",
                e,
                exc_info=True
            )
            return "Error al intentar registrar el pago", False, None

        finally:
            connection.close()
