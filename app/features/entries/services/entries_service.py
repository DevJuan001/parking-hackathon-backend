from app.utils.logger import get_logger
from app.core.exception import ServiceError
from app.core.database import get_connection
from app.utils.plate_formatter import plate_formatter
from app.features.entries.repositories.entries_repository import EntriesRepository
from app.features.parking.repositories.plates_repository import PlatesRepository
from app.features.spots.repositories.spots_repository import SpotsRepository
from app.features.entries.models.entries_schemas import CreateEntrySchema, EntriesFiltersSchema

logger = get_logger("entries.service")


class EntriesService:

    @staticmethod
    def get_all_entries(parking_id: int, filters: EntriesFiltersSchema):
        connection = get_connection()

        try:
            error, entries = EntriesRepository.find_all_entries(
                parking_id, filters, connection
            )

            if error:
                raise ServiceError(error)

            return None, entries

        except ServiceError as e:
            return e.message, None

        except Exception as e:
            logger.error(
                "Error en get_all_entries: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener los ingresos", None

        finally:
            connection.close()

    @staticmethod
    def get_entry_by_id(parking_id: int, entry_id: int):
        connection = get_connection()

        try:
            error, entry = EntriesRepository.find_entry_by_id(
                parking_id, entry_id, connection
            )

            if error or not entry:
                raise ServiceError(error)

            return None, entry

        except ServiceError as e:
            return e.message, None

        except Exception as e:
            logger.error(
                "Error en get_entry_by_id: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener el ingreso", None

        finally:
            connection.close()

    @staticmethod
    def get_recent_entries(parking_id: int):
        connection = get_connection()

        try:
            error, entries = EntriesRepository.find_recent_entries(
                parking_id, connection
            )

            if error:
                raise ServiceError(error)

            return None, entries

        except ServiceError as e:
            return e.message, None

        except Exception as e:
            logger.error(
                "Error en get_recent_entries: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener los ingresos recientes", None

        finally:
            connection.close()

    @staticmethod
    def get_entry_stats(parking_id: int):
        connection = get_connection()

        try:
            error, stats = EntriesRepository.count_entry_stats(
                parking_id, connection
            )

            if error:
                raise ServiceError(error)

            return None, stats

        except ServiceError as e:
            return e.message, None

        except Exception as e:
            logger.error(
                "Error en get_entry_stats: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener las estadisticas de ingresos", None

        finally:
            connection.close()

    @staticmethod
    def get_entries_by_plate(parking_id: int, plate_id: int):
        connection = get_connection()

        try:
            error, entries = EntriesRepository.find_entries_by_plate(
                parking_id, plate_id, connection
            )

            if error:
                raise ServiceError(error)

            return None, entries

        except ServiceError as e:
            return e.message, None

        except Exception as e:
            logger.error(
                "Error en get_entries_by_plate: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener los ingresos de la placa", None

        finally:
            connection.close()

    @staticmethod
    async def create_entry(parking_id: int, entry_data: CreateEntrySchema):
        data = entry_data.model_dump()

        connection = get_connection()

        try:
            plate_text = plate_formatter(data["plate"])

            if not plate_text:
                raise ServiceError("La placa no puede estar vacía")

            if len(plate_text) != 6:
                raise ServiceError("La placa debe tener 6 caracteres")

            if not plate_text[:3].isalpha():
                raise ServiceError("La placa debe iniciar con tres letras")

            if plate_text[-1].isalpha():
                vehicle_type_id = 2
            else:
                vehicle_type_id = 1

            error, plate_list = PlatesRepository.get_plate_by_name(
                parking_id, plate_text, connection
            )

            if error:
                raise ServiceError(error)

            plate = plate_list[0] if plate_list else None

            if not plate:
                error, new_plate_id, message = PlatesRepository.create_plate(
                    parking_id=parking_id,
                    plate_str=plate_text,
                    vehicle_type_id=vehicle_type_id,
                    connection=connection
                )

                if error or not new_plate_id:
                    raise ServiceError(error or "Error al registrar la placa")

                plate_id = new_plate_id
                plate_vehicle_type_id = vehicle_type_id

            else:
                plate_id = plate.id
                plate_vehicle_type_id = plate.vehicle_type

            error, active = EntriesRepository.has_active_entry(
                parking_id, plate_id, connection
            )

            if error:
                raise ServiceError(error)

            if active:
                raise ServiceError("La placa ya tiene un ingreso activo")

            error, spot_id, spot_label, floor_name = SpotsRepository.find_available_spot(
                parking_id, plate_vehicle_type_id, connection
            )

            if error or not spot_id:
                raise ServiceError(error or "No hay plazas disponibles")

            error, success, message = EntriesRepository.create_entry(
                parking_id=parking_id,
                plate_id=plate_id,
                spot_id=spot_id,
                connection=connection
            )

            if error or not success:
                raise ServiceError(error)

            error, success, message = SpotsRepository.update_spot_status(
                parking_id, spot_id, 3, connection
            )

            if error or not success:
                raise ServiceError(error)

            connection.commit()

            return None, True, f"Dirigete al {floor_name} y a la plaza {spot_label}"

        except ServiceError as e:
            connection.rollback()
            return e.message, False, None

        except Exception as e:
            connection.rollback()
            logger.error(
                "Error en create_entry: %s",
                e,
                exc_info=True
            )
            return "Error al intentar registrar el ingreso", False, None

        finally:
            connection.close()
