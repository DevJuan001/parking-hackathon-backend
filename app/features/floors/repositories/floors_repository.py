from app.utils.logger import get_logger
from app.utils.date_formatter import date_formatter
from app.features.floors.models.floors_responses import FloorResponse

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
                    id=item[0],
                    name=item[1],
                    created_at=date_formatter(item[2])
                )
                for item in results
            ]
            return None, floors

        except Exception as e:
            logger.error("Error en find_all_floors: %s", e, exc_info=True)
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
                id=result[0],
                name=result[1],
                created_at=date_formatter(result[2])
            )
            return None, floor

        except Exception as e:
            logger.error("Error en find_floor_by_id: %s", e, exc_info=True)
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

        except Exception as e:
            logger.error("Error en find_floor_id_by_name: %s", e, exc_info=True)
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

        except Exception as e:
            logger.error("Error en create_floor: %s", e, exc_info=True)
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

        except Exception as e:
            logger.error("Error en update_floor: %s", e, exc_info=True)
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

        except Exception as e:
            logger.error("Error en delete_floor: %s", e, exc_info=True)
            return "Error al intentar eliminar el piso", False, None

        finally:
            cursor.close()
