from app.utils.logger import get_logger
from app.core.exception import ServiceError
from app.core.database import get_connection
from app.tasks.knowledge_tasks import rebuild_parking_knowledge
from app.features.tariffs.repositories.tariffs_repository import TariffsRepository
from app.features.tariffs.models.tariffs_schemas import CreateTariffSchema, UpdateTariffSchema

logger = get_logger("tariffs.service")


class TariffsService:

    @staticmethod
    def get_all_tariffs(parking_id: int):
        connection = get_connection()

        try:
            error, tariffs = TariffsRepository.find_all_tariffs(
                parking_id, connection
            )

            if error:
                raise ServiceError(error)

            return None, tariffs

        except ServiceError as e:
            return e.message, None

        except Exception as e:
            logger.error(
                "Error en get_all_tariffs: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener las tarifas", None

        finally:
            connection.close()

    @staticmethod
    def get_tariff_by_id(parking_id: int, tariff_id: int):
        connection = get_connection()

        try:
            error, tariff = TariffsRepository.find_tariff_by_id(
                parking_id, tariff_id, connection
            )

            if error or not tariff:
                raise ServiceError(error)

            return None, tariff

        except ServiceError as e:
            return e.message, None

        except Exception as e:
            logger.error(
                "Error en get_tariff_by_id: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener la tarifa", None

        finally:
            connection.close()

    @staticmethod
    def get_available_vehicle_types(parking_id: int):
        connection = get_connection()

        try:
            error, vehicle_types = (
                TariffsRepository.find_vehicle_types_without_tariff(
                    parking_id, connection
                )
            )

            if error:
                raise ServiceError(error)

            return None, vehicle_types

        except ServiceError as e:
            return e.message, None

        except Exception as e:
            logger.error(
                "Error en get_available_vehicle_types: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener los tipos de vehículo disponibles", None

        finally:
            connection.close()

    @staticmethod
    def find_tariff_id_by_vehicle_type(parking_id: int, vehicle_type_id: int):
        connection = get_connection()

        try:
            error, tariff_id = TariffsRepository.find_tariff_id_by_vehicle_type(
                parking_id, vehicle_type_id, connection
            )

            if error or not tariff_id:
                return error or "Tarifa no encontrada para ese tipo de vehículo", None

            return None, tariff_id

        except Exception as e:
            logger.error(
                "Error en find_tariff_id_by_vehicle_type: %s", e, exc_info=True
            )
            return "Error al buscar la tarifa por tipo de vehículo", None

        finally:
            connection.close()

    @staticmethod
    async def create_tariff(parking_id: int, tariff_data: CreateTariffSchema):
        connection = get_connection()

        try:
            error, success, message = TariffsRepository.create_tariff(
                parking_id=parking_id,
                vehicle_type_id=tariff_data.vehicle_type,
                value=tariff_data.value,
                connection=connection
            )

            if error or not success:
                raise ServiceError(error)

            connection.commit()

            rebuild_parking_knowledge.delay(
                parking_id=parking_id
            )

            return None, True, "Tarifa creada correctamente"

        except ServiceError as e:
            connection.rollback()
            return e.message, False, None

        except Exception as e:
            connection.rollback()
            logger.error(
                "Error en create_tariff: %s",
                e,
                exc_info=True
            )
            return "Error al intentar crear la tarifa", False, None

        finally:
            connection.close()

    @staticmethod
    def update_tariff(parking_id: int, tariff_id: int, tariff_data: UpdateTariffSchema):
        connection = get_connection()

        try:
            error, existing = TariffsRepository.find_tariff_by_id(
                parking_id, tariff_id, connection
            )

            if not existing:
                raise ServiceError("Tarifa no encontrada")

            if not tariff_data:
                raise ServiceError("Debes enviar el valor a actualizar")

            error, success, message = TariffsRepository.update_tariff(
                parking_id, tariff_data, connection
            )

            if error or not success:
                raise ServiceError(error)

            connection.commit()

            rebuild_parking_knowledge.delay(parking_id)
            return None, True, "Tarifa actualizada correctamente"

        except ServiceError as e:
            connection.rollback()
            return e.message, False, None

        except Exception as e:
            connection.rollback()
            logger.error(
                "Error en update_tariff: %s",
                e,
                exc_info=True
            )
            return "Error al intentar actualizar la tarifa", False, None

        finally:
            connection.close()

    @staticmethod
    def delete_tariff(parking_id: int, tariff_id: int):
        connection = get_connection()

        try:
            # Validamos que la tarifa exista
            error, existing = TariffsRepository.find_tariff_by_id(
                parking_id, tariff_id, connection
            )

            if error or not existing:
                raise ServiceError(
                    "No se encontro la tarifa solicitada, verifica el id e intentalo nuevamente"
                )

            # Verificamos que no haya vehiculos activos de este tipo dentro del parking
            error, active_count = TariffsRepository.count_active_vehicles_by_type(
                parking_id, existing.vehicle_type, connection
            )

            if error:
                raise ServiceError(error)

            if active_count > 0:
                raise ServiceError(
                    f"No se puede eliminar la tarifa porque hay {active_count} "
                    f"vehiculo(s) del mismo tipo dentro del parking. "
                    f"Registra su salida y vuelve a intentarlo"
                )

            error, success, message = TariffsRepository.delete_tariff(
                parking_id, tariff_id, connection
            )

            if error or not success:
                raise ServiceError(error or "Tarifa no encontrada")

            connection.commit()

            rebuild_parking_knowledge.delay(parking_id)
            return None, True, message

        except ServiceError as e:
            connection.rollback()
            return e.message, False, None

        except Exception as e:
            connection.rollback()
            logger.error(
                "Error en delete_tariff: %s",
                e,
                exc_info=True
            )
            return "Error al intentar eliminar la tarifa", False, None

        finally:
            connection.close()
