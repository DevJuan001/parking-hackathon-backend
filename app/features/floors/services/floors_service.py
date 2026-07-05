from app.utils.logger import get_logger
from app.core.exception import ServiceError
from app.core.database import get_connection
from app.features.floors.repositories.floors_repository import FloorsRepository
from app.features.spots.repositories.spots_repository import SpotsRepository

logger = get_logger("floors.service")


class FloorsService:

    @staticmethod
    def get_all_floors(parking_id: int):
        connection = get_connection()

        try:
            error, floors = FloorsRepository.find_all_floors(
                parking_id, connection
            )

            if error:
                raise ServiceError(error)

            return None, floors

        except ServiceError as e:
            return e.message, None

        except Exception as e:
            logger.error(
                "Error en get_all_floors: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener los pisos", None

        finally:
            connection.close()

    @staticmethod
    def get_floor_by_id(parking_id: int, floor_id: int):
        connection = get_connection()

        try:
            error, floor = FloorsRepository.find_floor_by_id(
                parking_id, floor_id, connection
            )

            if error or not floor:
                raise ServiceError(error)

            return None, floor

        except ServiceError as e:
            return e.message, None

        except Exception as e:
            logger.error(
                "Error en get_floor_by_id: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener el piso", None

        finally:
            connection.close()

    @staticmethod
    def create_floor(parking_id: int, name: str):
        connection = get_connection()

        try:
            full_name = _format_floor_name(name)

            error, floor_id, message = FloorsRepository.create_floor(
                parking_id, full_name, connection
            )

            if error or not floor_id:
                raise ServiceError(error)

            connection.commit()

            return None, True, message

        except ServiceError as e:
            connection.rollback()
            return e.message, False, None

        except Exception as e:
            connection.rollback()
            logger.error(
                "Error en create_floor: %s",
                e,
                exc_info=True
            )
            return "Error al intentar registrar el piso", False, None

        finally:
            connection.close()

    @staticmethod
    def update_floor(parking_id: int, floor_id: int, name: str):
        connection = get_connection()

        try:
            full_name = _format_floor_name(name)

            error, exists = FloorsRepository.find_floor_by_id(
                parking_id, floor_id, connection
            )

            if error or not exists:
                raise ServiceError(
                    "No se encontro el piso solicitado, verifica el id e intentalo nuevamente"
                )

            error, success, message = FloorsRepository.update_floor(
                parking_id, floor_id, full_name, connection
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
                "Error en update_floor: %s",
                e,
                exc_info=True
            )
            return "Error al intentar actualizar el piso", False, None

        finally:
            connection.close()

    @staticmethod
    def delete_floor(parking_id: int, floor_id: int):
        connection = get_connection()

        try:
            # Validamos que el piso exista
            error, existing = FloorsRepository.find_floor_by_id(
                parking_id, floor_id, connection
            )

            if error or not existing:
                raise ServiceError(
                    "No se encontro el piso solicitado, verifica el id e intentalo nuevamente"
                )

            # Verificamos que ninguna plaza del piso este ocupada (spot_status = 3)
            error, occupied_count = SpotsRepository.count_occupied_spots_by_floor(
                parking_id, floor_id, connection
            )

            if error:
                raise ServiceError(error)

            if occupied_count > 0:
                raise ServiceError(
                    f"No se puede eliminar el piso porque hay {occupied_count} "
                    f"plaza(s) ocupada(s). Registra la salida de los vehiculos "
                    f"y vuelve a intentarlo"
                )

            # Borramos primero todas las plazas del piso
            error, spots_ok, _ = SpotsRepository.delete_spots_by_floor(
                parking_id, floor_id, connection
            )

            if error or not spots_ok:
                raise ServiceError(
                    error or "No se pudieron eliminar las plazas del piso"
                )

            # Luego borramos el piso
            error, success, message = FloorsRepository.delete_floor(
                parking_id, floor_id, connection
            )

            if error or not success:
                raise ServiceError(error or "Piso no encontrado")

            connection.commit()

            return None, True, message

        except ServiceError as e:
            connection.rollback()
            return e.message, False, None

        except Exception as e:
            connection.rollback()
            logger.error(
                "Error en delete_floor: %s",
                e,
                exc_info=True
            )
            return "Error al intentar eliminar el piso", False, None

        finally:
            connection.close()


def _format_floor_name(name: str) -> str:
    cleaned = name.strip()
    if not cleaned:
        raise ServiceError(
            "El nombre del piso no puede estar vacio, ingresa un valor e intentalo nuevamente"
        )
    if "piso" in cleaned.lower():
        return cleaned
    return f"Piso {cleaned}"
