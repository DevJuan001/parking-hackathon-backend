from app.utils.logger import get_logger
from app.utils.date_formatter import date_formatter
from app.features.spots.models.spots_schemas import SpotsFiltersSchema
from app.features.spots.models.spots_responses import SpotResponse

logger = get_logger("spots.repository")


class SpotsRepository:

    @staticmethod
    def find_all_spots(parking_id: int, filters_data: SpotsFiltersSchema, connection):
        data = filters_data.model_dump(exclude_none=True)

        cursor = connection.cursor()

        query = """
        SELECT
            s.spot_id,
            s.floor_id,
            s.spot,
            s.spot_status,
            s.created_at,
            s.vehicle_type_id,
            (
                SELECT p.plate
                FROM ENTRIES AS e
                INNER JOIN PLATES AS p ON p.id = e.plate_id
                WHERE e.spot_id = s.spot_id
                  AND NOT EXISTS (
                      SELECT 1 FROM EXITS AS x
                      WHERE x.plate_id = e.plate_id
                        AND x.created_at > e.created_at
                  )
                ORDER BY e.created_at DESC
                LIMIT 1
            ) AS plate
        FROM SPOTS AS s
        INNER JOIN FLOORS AS f
        ON f.id = s.floor_id
        """

        filters = ["f.parking_id = %s"]
        values = [parking_id]

        if "spot_status" in data:
            filters.append("s.spot_status = %s")
            values.append(data["spot_status"])

        if "floor_id" in data:
            filters.append("s.floor_id = %s")
            values.append(data["floor_id"])

        query += " WHERE " + " AND ".join(filters)

        try:
            cursor.execute(query, values)
            results = cursor.fetchall()

            spots = [
                SpotResponse(
                    spot_id=item[0],
                    floor_id=item[1],
                    spot=item[2],
                    spot_status=item[3],
                    created_at=date_formatter(item[4]),
                    vehicle_type_id=item[5],
                    plate=item[6]
                )
                for item in results
            ]
            return None, spots

        except Exception as e:
            logger.error("Error en find_all_spots: %s", e, exc_info=True)
            return "Error al intentar obtener las plazas", None

        finally:
            cursor.close()

    @staticmethod
    def find_spot_by_id(parking_id: int, spot_id: int, connection):
        cursor = connection.cursor()

        query = """
        SELECT
            s.spot_id,
            s.floor_id,
            s.spot,
            s.spot_status,
            s.created_at,
            s.vehicle_type_id,
            (
                SELECT p.plate
                FROM ENTRIES AS e
                INNER JOIN PLATES AS p ON p.id = e.plate_id
                WHERE e.spot_id = s.spot_id
                  AND NOT EXISTS (
                      SELECT 1 FROM EXITS AS x
                      WHERE x.plate_id = e.plate_id
                        AND x.created_at > e.created_at
                  )
                ORDER BY e.created_at DESC
                LIMIT 1
            ) AS plate
        FROM SPOTS AS s
        INNER JOIN FLOORS AS f ON f.id = s.floor_id
        WHERE f.parking_id = %s AND s.spot_id = %s
        """

        try:
            cursor.execute(query, (parking_id, spot_id))
            result = cursor.fetchone()

            if not result:
                return "Plaza no encontrada", None

            spot = SpotResponse(
                spot_id=result[0],
                floor_id=result[1],
                spot=result[2],
                spot_status=result[3],
                created_at=date_formatter(result[4]),
                vehicle_type_id=result[5],
                plate=result[6]
            )
            return None, spot

        except Exception as e:
            logger.error("Error en find_spot_by_id: %s", e, exc_info=True)
            return "Error al intentar obtener la plaza", None

        finally:
            cursor.close()

    @staticmethod
    def find_available_spot(parking_id: int, vehicle_type_id: int, connection):
        cursor = connection.cursor()

        query = """
        SELECT s.spot_id, s.spot, f.name
        FROM SPOTS AS s
        INNER JOIN FLOORS AS f ON f.id = s.floor_id
        WHERE f.parking_id = %s
          AND s.spot_status = 2
          AND s.vehicle_type_id = %s
        LIMIT 1
        """

        try:
            cursor.execute(query, (parking_id, vehicle_type_id))
            result = cursor.fetchone()

            if not result:
                return "Lo sentimos, no hay plazas disponibles para este tipo de vehículo", None, None, None,

            return None, result[0], result[1], result[2]

        except Exception as e:
            logger.error("Error en find_available_spot: %s", e, exc_info=True)
            return "Error al buscar plaza disponible", None, None, None

        finally:
            cursor.close()

    @staticmethod
    def create_spot(
        floor_id: int,
        spot_label: str,
        vehicle_type_id: int,
        connection,
    ):
        cursor = connection.cursor()

        query = """
        INSERT INTO SPOTS (floor_id, spot, spot_status, vehicle_type_id)
        VALUES (%s, %s, 2, %s)
        """

        try:
            cursor.execute(query, (floor_id, spot_label, vehicle_type_id))
            return None, True, "Plaza registrada correctamente"

        except Exception as e:
            logger.error("Error en create_spot: %s", e, exc_info=True)
            return "Error al intentar registrar la plaza", False, None

        finally:
            cursor.close()

    @staticmethod
    def update_spot_status(parking_id: int, spot_id: int, status: int, connection):
        cursor = connection.cursor()

        query = """
        UPDATE SPOTS AS s
        INNER JOIN FLOORS AS f ON f.id = s.floor_id
        SET s.spot_status = %s
        WHERE f.parking_id = %s AND s.spot_id = %s
        """

        try:
            cursor.execute(query, (status, parking_id, spot_id))
            return None, True, "Estado de la plaza actualizado correctamente"

        except Exception as e:
            logger.error("Error en update_spot_status: %s", e, exc_info=True)
            return "Error al actualizar el estado de la plaza", False, None

        finally:
            cursor.close()

    @staticmethod
    def delete_spot(parking_id: int, spot_id: int, connection):
        cursor = connection.cursor()

        query = """
        DELETE s FROM SPOTS AS s
        INNER JOIN FLOORS AS f ON f.id = s.floor_id
        WHERE f.parking_id = %s AND s.spot_id = %s
        """

        try:
            cursor.execute(query, (parking_id, spot_id))

            if cursor.rowcount == 0:
                return "Plaza no encontrada", False, None

            return None, True, "Plaza eliminada correctamente"

        except Exception as e:
            logger.error("Error en delete_spot: %s", e, exc_info=True)
            return "Error al intentar eliminar la plaza", False, None

        finally:
            cursor.close()

    @staticmethod
    def count_occupied_spots_by_floor(
        parking_id: int, floor_id: int, connection
    ):
        cursor = connection.cursor()

        query = """
        SELECT COUNT(*)
        FROM SPOTS AS s
        INNER JOIN FLOORS AS f ON f.id = s.floor_id
        WHERE f.parking_id = %s AND s.floor_id = %s AND s.spot_status = 3
        """

        try:
            cursor.execute(query, (parking_id, floor_id))
            result = cursor.fetchone()
            count = int(result[0]) if result and result[0] is not None else 0
            return None, count

        except Exception as e:
            logger.error(
                "Error en count_occupied_spots_by_floor: %s", e, exc_info=True
            )
            return "Error al verificar plazas ocupadas del piso", 0

        finally:
            cursor.close()

    @staticmethod
    def delete_spots_by_floor(parking_id: int, floor_id: int, connection):
        cursor = connection.cursor()

        query = """
        DELETE s FROM SPOTS AS s
        INNER JOIN FLOORS AS f ON f.id = s.floor_id
        WHERE f.parking_id = %s AND s.floor_id = %s
        """

        try:
            cursor.execute(query, (parking_id, floor_id))
            return None, True, "Plazas del piso eliminadas correctamente"

        except Exception as e:
            logger.error(
                "Error en delete_spots_by_floor: %s", e, exc_info=True
            )
            return "Error al intentar eliminar las plazas del piso", False, None

        finally:
            cursor.close()

    @staticmethod
    def update_spot(
        parking_id: int,
        spot_id: int,
        floor_id: int | None,
        spot_label: str | None,
        spot_status: int | None,
        vehicle_type_id: int | None,
        connection,
    ):
        cursor = connection.cursor()

        SPOT_FIELDS = {
            "floor_id": "floor_id",
            "spot": "spot",
            "spot_status": "spot_status",
            "vehicle_type_id": "vehicle_type_id",
        }

        try:
            values: dict = {}

            if floor_id is not None:
                values["floor_id"] = floor_id

            if spot_label is not None:
                values["spot"] = spot_label

            if spot_status is not None:
                values["spot_status"] = spot_status

            if vehicle_type_id is not None:
                values["vehicle_type_id"] = vehicle_type_id

            if not values:
                return None, True, "Sin cambios para aplicar"

            set_clause = ", ".join(f"{col} = %s" for col in values.keys())
            params = list(values.values()) + [parking_id, spot_id]

            cursor.execute(
                f"""
                UPDATE SPOTS AS s
                INNER JOIN FLOORS AS f ON f.id = s.floor_id
                SET {set_clause}
                WHERE f.parking_id = %s AND s.spot_id = %s
                """,
                params,
            )

            return None, True, "Plaza actualizada correctamente"

        except Exception as e:
            logger.error("Error en update_spot: %s", e, exc_info=True)
            return "Error al actualizar la plaza", False, None

        finally:
            cursor.close()
