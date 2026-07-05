from app.utils.logger import get_logger
from app.core.exception import ServiceError
from app.core.database import get_connection
from app.features.floors.repositories.floors_repository import FloorsRepository
from app.features.parking.repositories.vehicle_types_repository import (
    VehicleTypesRepository,
)
from app.features.spots.repositories.spots_repository import SpotsRepository
from app.features.spots.models.spots_schemas import SpotsFiltersSchema

logger = get_logger("spots.service")


class SpotsService:

    @staticmethod
    def get_all_spots(parking_id: int, filters: SpotsFiltersSchema):
        connection = get_connection()

        try:
            error, spots = SpotsRepository.find_all_spots(
                parking_id, filters, connection
            )

            if error:
                raise ServiceError(error)

            return None, spots

        except ServiceError as e:
            return e.message, None

        except Exception as e:
            logger.error(
                "Error en get_all_spots: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener las plazas", None

        finally:
            connection.close()

    @staticmethod
    def get_spot_by_id(parking_id: int, spot_id: int):
        connection = get_connection()

        try:
            error, spot = SpotsRepository.find_spot_by_id(
                parking_id, spot_id, connection
            )

            if error or not spot:
                raise ServiceError(error)

            return None, spot

        except ServiceError as e:
            return e.message, None

        except Exception as e:
            logger.error(
                "Error en get_spot_by_id: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener la plaza", None

        finally:
            connection.close()

    @staticmethod
    def create_spot(
        parking_id: int,
        floor_id: int,
        spot_label: str,
        vehicle_type_id: int,
    ):
        connection = get_connection()

        try:
            error, floor = FloorsRepository.find_floor_by_id(
                parking_id, floor_id, connection
            )

            if error or not floor:
                raise ServiceError(error or "Piso no encontrado")

            error, existing_type = VehicleTypesRepository.find_vehicle_type_by_id(
                vehicle_type_id, connection
            )

            if error or not existing_type:
                raise ServiceError(
                    error or "Tipo de vehículo no encontrado, verifica el id e intentalo nuevamente"
                )

            error, success, message = SpotsRepository.create_spot(
                floor_id, spot_label, vehicle_type_id, connection
            )

            if error or not success:
                raise ServiceError(error)

            connection.commit()

            return None, True, "Plaza registrada correctamente"

        except ServiceError as e:
            connection.rollback()
            return e.message, False, None

        except Exception as e:
            connection.rollback()
            logger.error(
                "Error en create_spot: %s",
                e,
                exc_info=True
            )
            return "Error al intentar registrar la plaza", False, None

        finally:
            connection.close()

    @staticmethod
    def update_spot_status(parking_id: int, spot_id: int, status: int):
        connection = get_connection()

        try:
            error, success, message = SpotsRepository.update_spot_status(
                parking_id, spot_id, status, connection
            )

            if error or not success:
                raise ServiceError(error)

            connection.commit()

            return None, True, message

        except ServiceError as e:
            connection.rollback()
            return e.message, False, None

        except Exception as e:
            connection.rollback()
            logger.error(
                "Error en update_spot_status: %s",
                e,
                exc_info=True
            )
            return "Error al actualizar el estado de la plaza", False, None

        finally:
            connection.close()

    @staticmethod
    def update_spot(
        parking_id: int,
        spot_id: int,
        floor_id: int | None,
        spot_label: str | None,
        spot_status: int | None,
        vehicle_type_id: int | None,
    ):
        connection = get_connection()

        try:
            # Validamos que la plaza exista
            error, existing = SpotsRepository.find_spot_by_id(
                parking_id, spot_id, connection
            )

            if error or not existing:
                raise ServiceError(error or "Plaza no encontrada")

            # Si llega un floor_id, validamos que el piso exista
            if floor_id is not None:
                error, floor = FloorsRepository.find_floor_by_id(
                    parking_id, floor_id, connection
                )

                if error or not floor:
                    raise ServiceError(error or "Piso no encontrado")

            # Si llega un vehicle_type_id, validamos que exista
            if vehicle_type_id is not None:
                error, existing_type = (
                    VehicleTypesRepository.find_vehicle_type_by_id(
                        vehicle_type_id, connection
                    )
                )

                if error or not existing_type:
                    raise ServiceError(
                        error or "Tipo de vehículo no encontrado, verifica el id e intentalo nuevamente"
                    )

            error, success, message = SpotsRepository.update_spot(
                parking_id,
                spot_id,
                floor_id,
                spot_label,
                spot_status,
                vehicle_type_id,
                connection,
            )

            if error or not success:
                raise ServiceError(error)

            connection.commit()

            return None, True, message

        except ServiceError as e:
            connection.rollback()
            return e.message, False, None

        except Exception as e:
            connection.rollback()
            logger.error(
                "Error en update_spot: %s",
                e,
                exc_info=True
            )
            return "Error al actualizar la plaza", False, None

        finally:
            connection.close()

    @staticmethod
    def delete_spot(parking_id: int, spot_id: int):
        connection = get_connection()

        try:
            # Validamos que la plaza exista
            error, existing = SpotsRepository.find_spot_by_id(
                parking_id, spot_id, connection
            )

            if error or not existing:
                raise ServiceError(error or "Plaza no encontrada")

            # No se puede eliminar una plaza que está ocupada (spot_status = 3)
            if existing.spot_status == 3:
                raise ServiceError(
                    "La plaza esta ocupada, desocupala primero e intentalo nuevamente"
                )

            error, success, message = SpotsRepository.delete_spot(
                parking_id, spot_id, connection
            )

            if error or not success:
                raise ServiceError(error or "Plaza no encontrada")

            connection.commit()

            return None, True, message

        except ServiceError as e:
            connection.rollback()
            return e.message, False, None

        except Exception as e:
            connection.rollback()
            logger.error(
                "Error en delete_spot: %s",
                e,
                exc_info=True
            )
            return "Error al intentar eliminar la plaza", False, None

        finally:
            connection.close()
