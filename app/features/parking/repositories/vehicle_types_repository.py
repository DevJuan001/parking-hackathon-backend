from app.utils.logger import get_logger
from app.features.parking.models.parking_responses import VehicleTypeResponse

logger = get_logger("vehicle_types.repository")


class VehicleTypesRepository:

    @staticmethod
    def find_vehicle_type_id_by_name(name: str, connection):
        cursor = connection.cursor()

        query = "SELECT id FROM VEHICLE_TYPES WHERE name = %s"

        try:
            cursor.execute(query, (name,))
            result = cursor.fetchone()

            if not result:
                return "Tipo de vehículo no encontrado", None

            return None, result[0]

        except Exception as e:
            logger.error(
                "Error en find_vehicle_type_id_by_name: %s", e, exc_info=True
            )
            return "Error al buscar el tipo de vehículo", None

        finally:
            cursor.close()

    @staticmethod
    def find_vehicle_type_by_id(vehicle_type_id: int, connection):
        cursor = connection.cursor()

        query = "SELECT id FROM VEHICLE_TYPES WHERE id = %s"

        try:
            cursor.execute(query, (vehicle_type_id,))
            result = cursor.fetchone()

            if not result:
                return "Tipo de vehículo no encontrado", None

            return None, result[0]

        except Exception as e:
            logger.error(
                "Error en find_vehicle_type_by_id: %s", e, exc_info=True
            )
            return "Error al buscar el tipo de vehículo", None

        finally:
            cursor.close()

    @staticmethod
    def find_all_vehicle_types(connection):
        cursor = connection.cursor()

        query = "SELECT id, name FROM VEHICLE_TYPES ORDER BY id ASC"

        try:
            cursor.execute(query)
            results = cursor.fetchall()

            vehicle_types = [
                VehicleTypeResponse(id=item[0], name=item[1])
                for item in results
            ]
            return None, vehicle_types

        except Exception as e:
            logger.error(
                "Error en find_all_vehicle_types: %s", e, exc_info=True
            )
            return "Error al intentar obtener los tipos de vehículo", None

        finally:
            cursor.close()
