from app.utils.logger import get_logger
from app.features.exits.models.exits_responses import ExitResponse
from app.features.exits.models.exits_schemas import ExitsFiltersSchema

logger = get_logger("exits.repository")


class ExitsRepository:

    @staticmethod
    def find_all_exits(parking_id: int, filters_data: ExitsFiltersSchema, connection):
        cursor = connection.cursor()

        data = filters_data.model_dump(exclude_none=True)

        query = """
        SELECT
            e.id,
            p.plate,
            COALESCE(pay.value, 0) AS value,
            COALESCE(pm.name, 'No registrado') AS payment_method,
            e.created_at
        FROM EXITS AS e
        INNER JOIN PLATES AS p 
            ON p.id = e.plate_id
        LEFT JOIN PAYMENTS AS pay 
            ON pay.plate_id = e.plate_id
            AND pay.parking_id = e.parking_id
            AND pay.created_at = (
                SELECT MAX(p2.created_at)
                FROM PAYMENTS p2
                WHERE p2.parking_id = pay.parking_id
                  AND p2.plate_id   = pay.plate_id
            )
        LEFT JOIN PAYMENT_METHODS AS pm
            ON pm.id = pay.payment_method_id
        """

        filters = ["e.parking_id = %s"]
        values = [parking_id]

        if "plate_id" in data:
            filters.append("p.id = %s")
            values.append(data["plate_id"])

        if "start_date" in data:
            filters.append("DATE(e.created_at) >= %s")
            values.append(data["start_date"])

        if "end_date" in data:
            filters.append("DATE(e.created_at) <= %s")
            values.append(data["end_date"])

        if filters:
            query += " WHERE " + " AND ".join(filters)

        query += " ORDER BY e.id DESC LIMIT %s OFFSET %s"

        per_page = filters_data.per_page
        offset = (filters_data.page - 1) * per_page
        values += [per_page, offset]

        try:
            cursor.execute(query, values)
            results = cursor.fetchall()

            exits = [
                ExitResponse(
                    id=item[0],
                    plate=item[1],
                    value=item[2],
                    payment_method=item[3],
                    created_at=item[4]
                )
                for item in results
            ]
            return None, exits

        except Exception as e:
            logger.error("Error en find_all_exits: %s", e, exc_info=True)
            return "Error al intentar obtener las salidas", None

        finally:
            cursor.close()

    @staticmethod
    def find_exit_by_id(parking_id: int, exit_id: int, connection):
        cursor = connection.cursor()

        query = """
        SELECT
            e.id,
            p.plate,
            COALESCE(pay.value, 0) AS value,
            COALESCE(pm.name, 'No registrado') AS payment_method,
            e.created_at
        FROM EXITS AS e
        INNER JOIN PLATES AS p ON p.id = e.plate_id
        LEFT JOIN PAYMENTS AS pay ON pay.plate_id = e.plate_id
            AND pay.parking_id = e.parking_id
            AND pay.created_at = (
                SELECT MAX(p2.created_at)
                FROM PAYMENTS p2
                WHERE p2.parking_id = pay.parking_id
                  AND p2.plate_id   = pay.plate_id
            )
        LEFT JOIN PAYMENT_METHODS AS pm ON pm.id = pay.payment_method_id
        WHERE e.parking_id = %s AND e.id = %s
        """

        try:
            cursor.execute(query, (parking_id, exit_id))
            result = cursor.fetchone()

            if not result:
                return "Salida no encontrada", None

            return None, ExitResponse(
                id=result[0],
                plate=result[1],
                value=result[2],
                payment_method=result[3],
                created_at=result[4]
            )

        except Exception as e:
            logger.error("Error en find_exit_by_id: %s", e, exc_info=True)
            return "Error al intentar obtener la salida", None

        finally:
            cursor.close()

    @staticmethod
    def find_exits_by_plate(parking_id: int, plate_id: int, connection):
        cursor = connection.cursor()

        query = """
        SELECT
            e.id,
            p.plate,
            COALESCE(pay.value, 0) AS value,
            COALESCE(pm.name, 'No registrado') AS payment_method,
            e.created_at
        FROM EXITS AS e
        INNER JOIN PLATES AS p
            ON p.id = e.plate_id
        LEFT JOIN PAYMENTS AS pay ON pay.plate_id = e.plate_id
            AND pay.parking_id = e.parking_id
            AND pay.created_at = (
                SELECT MAX(p2.created_at)
                FROM PAYMENTS p2
                WHERE p2.parking_id = pay.parking_id
                  AND p2.plate_id   = pay.plate_id
            )
        LEFT JOIN PAYMENT_METHODS AS pm ON pm.id = pay.payment_method_id
        WHERE e.parking_id = %s AND e.plate_id = %s
        ORDER BY e.created_at DESC
        """

        try:
            cursor.execute(query, (parking_id, plate_id))
            results = cursor.fetchall()

            exits = [
                ExitResponse(
                    id=item[0],
                    plate=item[1],
                    value=item[2],
                    payment_method=item[3],
                    created_at=item[4]
                )
                for item in results
            ]
            return None, exits

        except Exception as e:
            logger.error("Error en find_exits_by_plate: %s", e, exc_info=True)
            return "Error al intentar obtener las salidas de la placa", None

        finally:
            cursor.close()

    @staticmethod
    def find_latest_exit(parking_id: int, plate_id: int, connection):
        cursor = connection.cursor()

        query = """
        SELECT
            e.id,
            p.plate,
            COALESCE(pay.value, 0) AS value,
            COALESCE(pm.name, 'No registrado') AS payment_method,
            e.created_at
        FROM EXITS AS e
        INNER JOIN PLATES AS p
            ON p.id = e.plate_id
        LEFT JOIN PAYMENTS AS pay ON pay.plate_id = e.plate_id
            AND pay.parking_id = e.parking_id
            AND pay.created_at = (
                SELECT MAX(p2.created_at)
                FROM PAYMENTS p2
                WHERE p2.parking_id = pay.parking_id
                  AND p2.plate_id   = pay.plate_id
            )
        LEFT JOIN PAYMENT_METHODS AS pm ON pm.id = pay.payment_method_id
        WHERE e.parking_id = %s AND e.plate_id = %s
        ORDER BY e.created_at DESC
        LIMIT 1
        """

        try:
            cursor.execute(query, (parking_id, plate_id))
            result = cursor.fetchone()

            if not result:
                return None, None

            return None, ExitResponse(
                id=result[0],
                plate=result[1],
                value=result[2],
                payment_method=result[3],
                created_at=result[4]
            )

        except Exception as e:
            logger.error("Error en find_latest_exit: %s", e, exc_info=True)
            return "Error al buscar la última salida", None

        finally:
            cursor.close()

    @staticmethod
    def create_exit(parking_id: int, plate_id: int, connection):
        cursor = connection.cursor()

        query = """
        INSERT INTO EXITS (parking_id, plate_id)
        VALUES (%s, %s)
        """

        try:
            cursor.execute(query, (parking_id, plate_id))
            return None, True, "Salida registrada correctamente"

        except Exception as e:
            logger.error("Error en create_exit: %s", e, exc_info=True)
            return "Error al intentar registrar la salida", False, None

        finally:
            cursor.close()

    @staticmethod
    def count_exit_stats(parking_id: int, connection):
        cursor = connection.cursor()

        query = """
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN DATE(e.created_at) = CURDATE() THEN 1 ELSE 0 END) AS today,
            SUM(CASE WHEN e.created_at >= (NOW() - INTERVAL 7 DAY) THEN 1 ELSE 0 END) AS this_week,
            SUM(
                CASE WHEN YEAR(e.created_at) = YEAR(CURDATE())
                          AND MONTH(e.created_at) = MONTH(CURDATE())
                     THEN 1 ELSE 0 END
            ) AS this_month
        FROM EXITS AS e
        WHERE e.parking_id = %s
        """

        try:
            cursor.execute(query, (parking_id,))
            result = cursor.fetchone()

            return None, {
                "total": int(result[0] or 0),
                "today": int(result[1] or 0),
                "this_week": int(result[2] or 0),
                "this_month": int(result[3] or 0)
            }

        except Exception as e:
            logger.error("Error en count_exit_stats: %s", e, exc_info=True)
            return "Error al intentar obtener las estadisticas de salidas", None

        finally:
            cursor.close()
