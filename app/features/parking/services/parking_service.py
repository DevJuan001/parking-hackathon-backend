from app.utils.logger import get_logger
from app.core.exception import ServiceError
from app.core.database import get_connection
from app.utils.plate_formatter import plate_formatter
from app.features.parking.models.parking_schemas import CreatePlateSchema
from app.features.parking.repositories.parkings_repository import ParkingsRepository
from app.features.parking.repositories.plates_repository import PlatesRepository
from app.features.parking.repositories.vehicle_types_repository import VehicleTypesRepository
from app.features.spots.models.spots_schemas import SpotsFiltersSchema
from app.features.spots.repositories.spots_repository import SpotsRepository

logger = get_logger("parking.service")


class ParkingService:

    @staticmethod
    def create_parking(name: str, country_id: int):
        connection = get_connection()

        try:
            if not name or not name.strip():
                raise ServiceError(
                    "El nombre del parking no puede estar vacío"
                )

            if not isinstance(country_id, int) or country_id <= 0:
                raise ServiceError(
                    "El pais del parking es obligatorio, selecciona uno e intentalo nuevamente"
                )

            error, success, parking_id = ParkingsRepository.create_parking(
                name=name.strip(),
                country_id=country_id,
                connection=connection
            )

            if error or not success or not parking_id:
                raise ServiceError(error or "No se pudo crear el parking")

            connection.commit()

            return None, parking_id, "Parking creado correctamente"

        except ServiceError as e:
            connection.rollback()
            return e.message, None, None

        except Exception as e:
            connection.rollback()
            logger.error(
                "Error en create_parking: %s",
                e,
                exc_info=True
            )
            return "Error al intentar crear el parking", None, None

        finally:
            connection.close()

    @staticmethod
    def get_all_plates(parking_id: int):
        connection = get_connection()

        try:
            error, plates = PlatesRepository.find_all_plates(
                parking_id, connection
            )

            if error:
                raise ServiceError(error)

            return None, plates

        except ServiceError as e:
            return e.message, None

        except Exception as e:
            logger.error(
                "Error en get_all_plates: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener las placas", None

        finally:
            connection.close()

    @staticmethod
    def get_all_vehicle_types():
        connection = get_connection()

        try:
            error, vehicle_types = VehicleTypesRepository.find_all_vehicle_types(
                connection
            )

            if error:
                raise ServiceError(error)

            return None, vehicle_types

        except ServiceError as e:
            return e.message, None

        except Exception as e:
            logger.error(
                "Error en get_all_vehicle_types: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener los tipos de vehículo", None

        finally:
            connection.close()

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
            return "Error al intentar obtener los espacios", None

        finally:
            connection.close()

    @staticmethod
    def get_plate_by_name(parking_id: int, plate: str):
        connection = get_connection()

        try:
            error, plate_response = PlatesRepository.get_plate_by_name(
                parking_id, plate, connection
            )

            if error:
                raise ServiceError(error)

            return None, plate_response

        except ServiceError as e:
            return e.message, None

        except Exception as e:
            logger.error(
                "Error en get_plate_by_name: %s",
                e,
                exc_info=True
            )
            return "Error al intentar buscar la placa", None

        finally:
            connection.close()

    @staticmethod
    async def create_plate(parking_id: int, plate_data: CreatePlateSchema):
        connection = get_connection()

        try:
            plate_text = plate_formatter(plate_data.plate)

            error, plate_exists = PlatesRepository.get_plate_by_name(
                parking_id, plate_text, connection
            )

            if error:
                raise ServiceError(error)

            if plate_exists:
                raise ServiceError(
                    "Esta placa ya se encuentra registrada, intenta cambiar la placa e intentalo nuevamente"
                )

            if not plate_text:
                raise ServiceError("La placa no puede estar vacía")

            if plate_text[-1].isalpha():
                vehicle_type = 2
            else:
                vehicle_type = 1

            error, vehicle_type_id = VehicleTypesRepository.find_vehicle_type_id_by_name(
                vehicle_type, connection
            )

            if error or not vehicle_type_id:
                raise ServiceError(error or "Tipo de vehículo no encontrado")

            error, plate_id, message = PlatesRepository.create_plate(
                parking_id=parking_id,
                plate_str=plate_text,
                vehicle_type_id=vehicle_type_id,
                connection=connection
            )

            if error or not plate_id:
                raise ServiceError(error or message)

            connection.commit()

            return None, True, "Placa registrada correctamente"

        except ServiceError as e:
            connection.rollback()
            return e.message, False, None

        except Exception as e:
            connection.rollback()
            logger.error(
                "Error en create_plate: %s",
                e,
                exc_info=True
            )
            return "Error al intentar registrar la placa", False, None

        finally:
            connection.close()

    @staticmethod
    def update_parking(parking_id: int, name=None, address=None, phone=None):
        connection = get_connection()

        clean_name = name.strip() if name else None
        clean_address = address.strip() if address else None
        clean_phone = phone.strip() if phone else None

        if clean_name is not None and len(clean_name) > 100:
            return "El nombre del parking es demasiado largo (máx 100 caracteres)", False, None

        if clean_address is not None and len(clean_address) > 200:
            return "La dirección es demasiado larga (máx 200 caracteres)", False, None

        if clean_phone is not None and len(clean_phone) > 20:
            return "El teléfono es demasiado largo (máx 20 caracteres)", False, None

        if clean_name is not None and not clean_name:
            return "El nombre no puede estar vacío", False, None

        if clean_address is not None and not clean_address:
            return "La dirección no puede estar vacía", False, None

        if clean_phone is not None and not clean_phone:
            return "El teléfono no puede estar vacío", False, None

        try:
            error, updated = ParkingsRepository.update_parking(
                parking_id=parking_id,
                connection=connection,
                name=clean_name,
                address=clean_address,
                phone=clean_phone,
            )

            if error:
                raise ServiceError(error)

            if not updated:
                raise ServiceError(
                    "No se encontró el parking o no se realizaron cambios"
                )

            connection.commit()

            return None, True, "Parking actualizado correctamente"

        except ServiceError as e:
            connection.rollback()
            return e.message, False, None

        except Exception as e:
            connection.rollback()
            logger.error(
                "Error en update_parking: %s",
                e,
                exc_info=True
            )
            return "Error al intentar actualizar el parking", False, None

        finally:
            connection.close()
