from app.utils.logger import get_logger
from app.utils.date_formatter import date_formatter
from app.features.parking.models.parking_responses import PlateResponse

logger = get_logger("plates.repository")


class PlatesRepository:

    @staticmethod
    def find_all_plates(parking_id: int, connection):
        cursor = connection.cursor()

        query = """
        SELECT
            p.id,
            p.plate,
            vt.id,
            p.created_at
        FROM PLATES AS p
        INNER JOIN VEHICLE_TYPES AS vt
            ON vt.id = p.vehicle_type_id
        WHERE p.parking_id = %s
        ORDER BY p.created_at DESC
        """

        try:
            cursor.execute(query, (parking_id,))
            results = cursor.fetchall()

            plates = [
                PlateResponse(
                    id=item[0],
                    plate=item[1],
                    vehicle_type=item[2],
                    created_at=date_formatter(item[3])
                )
                for item in results
            ]
            return None, plates

        except Exception as e:
            logger.error("Error en find_all_plates: %s", e, exc_info=True)
            return "Error al intentar obtener las placas", None

        finally:
            cursor.close()

    @staticmethod
    def find_plate_by_id(parking_id: int, plate_id: int, connection):
        cursor = connection.cursor()

        query = """
        SELECT
            p.id,
            p.plate,
            vt.name,
            p.created_at
        FROM PLATES AS p
        INNER JOIN VEHICLE_TYPES AS vt ON vt.id = p.vehicle_type_id
        WHERE p.parking_id = %s AND p.id = %s
        """

        try:
            cursor.execute(query, (parking_id, plate_id))
            result = cursor.fetchone()

            if not result:
                return "Placa no encontrada", None

            plate = PlateResponse(
                id=result[0],
                plate=result[1],
                vehicle_type=result[2],
                created_at=date_formatter(result[3])
            )
            return None, plate

        except Exception as e:
            logger.error("Error en find_plate_by_id: %s", e, exc_info=True)
            return "Error al intentar obtener la placa", None

        finally:
            cursor.close()


    @staticmethod
    def get_plate_by_name(parking_id: int, plate: str, connection):
        cursor = connection.cursor()

        query = """
        SELECT
            p.id,
            p.plate,
            vt.id,
            p.created_at
        FROM PLATES AS p
        INNER JOIN VEHICLE_TYPES AS vt ON vt.id = p.vehicle_type_id
        WHERE p.parking_id = %s AND p.plate = %s
        """

        try:
            cursor.execute(query, (parking_id, plate.upper()))
            result = cursor.fetchall()

            if not result:
                return None, None

            plate_response = [
                PlateResponse(
                    id=item[0],
                    plate=item[1],
                    vehicle_type=item[2],
                    created_at=date_formatter(item[3])
                )
                for item in result
            ]

            return None, plate_response

        except Exception as e:
            logger.error("Error en get_plate_by_name: %s", e, exc_info=True)
            return "Error al intentar buscar la placa", None

        finally:
            cursor.close()

    @staticmethod
    def create_plate(parking_id: int, plate_str: str, vehicle_type_id: int, connection):
        cursor = connection.cursor()

        query = """
        INSERT INTO PLATES (parking_id, plate, vehicle_type_id)
        VALUES (%s, %s, %s)
        """

        try:
            cursor.execute(query, (parking_id, plate_str, vehicle_type_id))
            return None, cursor.lastrowid, "Placa registrada correctamente"

        except Exception as e:
            logger.error("Error en create_plate: %s", e, exc_info=True)
            return "Error al intentar registrar la placa", None, None

        finally:
            cursor.close()

    @staticmethod
    def update_plate_vehicle_type(parking_id: int, plate_id: int, vehicle_type_id: int, connection):
        cursor = connection.cursor()

        query = """
        UPDATE PLATES
        SET vehicle_type_id = %s
        WHERE parking_id = %s AND id = %s
        """

        try:
            cursor.execute(query, (vehicle_type_id, parking_id, plate_id))
            return None, True

        except Exception as e:
            logger.error("Error en update_plate_vehicle_type: %s", e, exc_info=True)
            return "Error al actualizar el tipo de vehículo", False

        finally:
            cursor.close()
