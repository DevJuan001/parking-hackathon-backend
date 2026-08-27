import json

from app.features.floors.models.floors_responses import FloorResponse
from app.utils.date_formatter import date_formatter
from app.utils.logger import get_logger

logger = get_logger("floors.repository")


class FloorsRepository:
    @staticmethod
    def find_all_floors(parking_id: int, connection):
        cursor = connection.cursor()

        query = """
        SELECT
            id,
            name,
            created_at
        FROM FLOORS
        WHERE parking_id = %s
        ORDER BY name ASC
        """

        try:
            cursor.execute(query, (parking_id,))
            results = cursor.fetchall()

            floors = [
                FloorResponse(
                    id=item[0], name=item[1], created_at=date_formatter(item[2])
                )
                for item in results
            ]
            return None, floors

        except Exception:
            logger.exception("Error en find_all_floors")
            return "Error al intentar obtener los pisos", None

        finally:
            cursor.close()

    @staticmethod
    def find_floor_by_id(parking_id: int, floor_id: int, connection):
        cursor = connection.cursor()

        query = """
        SELECT
            id,
            name,
            created_at
        FROM FLOORS
        WHERE parking_id = %s AND id = %s
        """

        try:
            cursor.execute(query, (parking_id, floor_id))
            result = cursor.fetchone()

            if not result:
                return "Piso no encontrado", None

            floor = FloorResponse(
                id=result[0], name=result[1], created_at=date_formatter(result[2])
            )
            return None, floor

        except Exception:
            logger.exception("Error en find_floor_by_id")
            return "Error al intentar obtener el piso", None

        finally:
            cursor.close()

    @staticmethod
    def find_floor_id_by_name(parking_id: int, name: str, connection):
        cursor = connection.cursor()

        query = """
        SELECT id
        FROM FLOORS
        WHERE parking_id = %s AND name = %s
        LIMIT 1
        """

        try:
            cursor.execute(query, (parking_id, name))
            result = cursor.fetchone()

            if not result:
                return "Piso no encontrado", None

            return None, result[0]

        except Exception:
            logger.exception("Error en find_floor_id_by_name")
            return "Error al buscar el piso por nombre", None

        finally:
            cursor.close()

    @staticmethod
    def create_floor(parking_id: int, name: str, connection):
        cursor = connection.cursor()

        query = """
        INSERT INTO FLOORS (parking_id, name)
        VALUES (%s, %s)
        """

        try:
            cursor.execute(query, (parking_id, name))
            return None, cursor.lastrowid, "Piso registrado correctamente"

        except Exception:
            logger.exception("Error en create_floor")
            return "Error al intentar registrar el piso", None, None

        finally:
            cursor.close()

    @staticmethod
    def update_floor(parking_id: int, floor_id: int, name: str, connection):
        cursor = connection.cursor()

        query = """
        UPDATE FLOORS
        SET name = %s
        WHERE parking_id = %s AND id = %s
        """

        try:
            cursor.execute(query, (name, parking_id, floor_id))
            return None, True, "Piso actualizado correctamente"

        except Exception:
            logger.exception("Error en update_floor")
            return "Error al intentar actualizar el piso", False, None

        finally:
            cursor.close()

    @staticmethod
    def delete_floor(parking_id: int, floor_id: int, connection):
        cursor = connection.cursor()

        query = """
        DELETE FROM FLOORS
        WHERE parking_id = %s AND id = %s
        """

        try:
            cursor.execute(query, (parking_id, floor_id))

            if cursor.rowcount == 0:
                return "Piso no encontrado", False, None

            return None, True, "Piso eliminado correctamente"

        except Exception:
            logger.exception("Error en delete_floor")
            return "Error al intentar eliminar el piso", False, None

        finally:
            cursor.close()

    @staticmethod
    def find_all_floors_with_spots(parking_id: int, connection):
        cursor = connection.cursor()

        query = """
        SELECT f.id, f.name, JSON_ARRAYAGG(s.spot)
        FROM FLOORS AS f
        LEFT JOIN SPOTS AS s ON s.floor_id = f.id
        WHERE f.parking_id = %s
        GROUP BY f.id, f.name
        ORDER BY f.name ASC
        """

        try:
            cursor.execute(query, (parking_id,))
            rows = cursor.fetchall()

            result = []
            for floor_id, name, spots_json in rows:
                spots = json.loads(spots_json) if spots_json else []
                result.append((floor_id, name, spots))

            return None, result

        except Exception:
            logger.exception("Error en find_all_floors_with_spots")
            return "Error al obtener los pisos con sus plazas", []

        finally:
            cursor.close()
