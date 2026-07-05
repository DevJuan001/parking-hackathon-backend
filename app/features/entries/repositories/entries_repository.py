from app.utils.logger import get_logger
from app.features.entries.models.entries_responses import EntryResponse, EntryStatsResponse
from app.features.entries.models.entries_schemas import EntriesFiltersSchema

logger = get_logger("entries.repository")


class EntriesRepository:

    @staticmethod
    def find_all_entries(parking_id: int, filters_data: EntriesFiltersSchema, connection):
        cursor = connection.cursor()

        data = filters_data.model_dump(exclude_none=True)

        query = """
        SELECT
            e.id,
            p.plate,
            vt.id,
            s.spot_id,
            s.spot,
            e.created_at
        FROM ENTRIES AS e
        INNER JOIN PLATES AS p 
            ON p.id  = e.plate_id
        INNER JOIN VEHICLE_TYPES AS vt
            ON vt.id = p.vehicle_type_id
        INNER JOIN SPOTS AS s 
            ON s.spot_id = e.spot_id
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

        query += " WHERE " + " AND ".join(filters)

        try:
            cursor.execute(query, values)
            results = cursor.fetchall()

            entries = [
                EntryResponse(
                    id=item[0],
                    plate=item[1],
                    vehicle_type=item[2],
                    spot_id=item[3],
                    spot=item[4],
                    created_at=item[5]
                )
                for item in results
            ]
            return None, entries

        except Exception as e:
            logger.error("Error en find_all_entries: %s", e, exc_info=True)
            return "Error al intentar obtener los ingresos", None

        finally:
            cursor.close()

    @staticmethod
    def find_entry_by_id(parking_id: int, entry_id: int, connection):
        cursor = connection.cursor()

        query = """
        SELECT
            e.id,
            p.plate,
            vt.name,
            s.spot_id,
            s.spot,
            e.created_at
        FROM ENTRIES AS e
        INNER JOIN PLATES        AS p  ON p.id  = e.plate_id
        INNER JOIN VEHICLE_TYPES AS vt ON vt.id = p.vehicle_type_id
        INNER JOIN SPOTS         AS s  ON s.spot_id = e.spot_id
        WHERE e.parking_id = %s AND e.id = %s
        """

        try:
            cursor.execute(query, (parking_id, entry_id))
            result = cursor.fetchone()

            if not result:
                return "Ingreso no encontrado", None

            entry = EntryResponse(
                id=result[0],
                plate=result[1],
                vehicle_type=result[2],
                spot_id=result[3],
                spot=result[4],
                created_at=result[5]
            )
            return None, entry

        except Exception as e:
            logger.error("Error en find_entry_by_id: %s", e, exc_info=True)
            return "Error al intentar obtener el ingreso", None

        finally:
            cursor.close()

    @staticmethod
    def find_recent_entries(parking_id: int, connection):
        cursor = connection.cursor()

        query = """
        SELECT
            e.id,
            p.plate,
            vt.id,
            s.spot_id,
            s.spot,
            e.created_at
        FROM ENTRIES AS e
        INNER JOIN PLATES        AS p  ON p.id  = e.plate_id
        INNER JOIN VEHICLE_TYPES AS vt ON vt.id = p.vehicle_type_id
        INNER JOIN SPOTS         AS s  ON s.spot_id = e.spot_id
        WHERE e.parking_id = %s
        ORDER BY e.created_at DESC
        LIMIT 5
        """

        try:
            cursor.execute(query, (parking_id,))
            results = cursor.fetchall()

            entries = [
                EntryResponse(
                    id=item[0],
                    plate=item[1],
                    vehicle_type=item[2],
                    spot_id=item[3],
                    spot=item[4],
                    created_at=item[5]
                )
                for item in results
            ]
            return None, entries

        except Exception as e:
            logger.error("Error en find_recent_entries: %s", e, exc_info=True)
            return "Error al intentar obtener los ingresos recientes", None

        finally:
            cursor.close()

    # Obtener estadisticas de ingresos del parking
    @staticmethod
    def count_entry_stats(parking_id: int, connection):
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
        FROM ENTRIES AS e
        WHERE e.parking_id = %s
        """

        try:
            cursor.execute(query, (parking_id,))
            result = cursor.fetchone()

            stats = EntryStatsResponse(
                total=int(result[0] or 0),
                today=int(result[1] or 0),
                this_week=int(result[2] or 0),
                this_month=int(result[3] or 0)
            )
            return None, stats

        except Exception as e:
            logger.error("Error en count_entry_stats: %s", e, exc_info=True)
            return "Error al intentar obtener las estadisticas de ingresos", None

        finally:
            cursor.close()

    @staticmethod
    def find_entries_by_plate(parking_id: int, plate_id: int, connection):
        cursor = connection.cursor()

        query = """
        SELECT
            e.id,
            p.plate,
            vt.name,
            s.spot_id,
            s.spot,
            e.created_at
        FROM ENTRIES AS e
        INNER JOIN PLATES        AS p  ON p.id  = e.plate_id
        INNER JOIN VEHICLE_TYPES AS vt ON vt.id = p.vehicle_type_id
        INNER JOIN SPOTS         AS s  ON s.spot_id = e.spot_id
        WHERE e.parking_id = %s AND e.plate_id = %s
        ORDER BY e.created_at DESC
        """

        try:
            cursor.execute(query, (parking_id, plate_id))
            results = cursor.fetchall()

            entries = [
                EntryResponse(
                    id=item[0],
                    plate=item[1],
                    vehicle_type=item[2],
                    spot_id=item[3],
                    spot=item[4],
                    created_at=item[5]
                )
                for item in results
            ]
            return None, entries

        except Exception as e:
            logger.error(
                "Error en find_entries_by_plate: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener los ingresos de la placa", None

        finally:
            cursor.close()

    @staticmethod
    def has_active_entry(parking_id: int, plate_id: int, connection):
        cursor = connection.cursor()

        query = """
        SELECT
            (SELECT MAX(e.created_at) FROM ENTRIES e WHERE e.parking_id = %s AND e.plate_id = %s) AS last_entry_at,
            (SELECT MAX(x.created_at) FROM EXITS   x WHERE x.parking_id = %s AND x.plate_id = %s) AS last_exit_at
        """

        try:
            cursor.execute(
                query, (parking_id, plate_id, parking_id, plate_id)
            )
            result = cursor.fetchone()

            last_entry_at = result[0] if result else None
            last_exit_at = result[1] if result else None

            is_active = last_entry_at is not None and (
                last_exit_at is None or last_entry_at > last_exit_at
            )

            return None, is_active

        except Exception as e:
            logger.error("Error en has_active_entry: %s", e, exc_info=True)
            return "Error al verificar si la placa tiene un ingreso activo", False

        finally:
            cursor.close()

    @staticmethod
    def find_latest_entry(parking_id: int, plate_id: int, connection):
        cursor = connection.cursor()

        query = """
        SELECT
            e.id,
            p.plate,
            vt.id,
            s.spot_id,
            s.spot,
            e.created_at
        FROM ENTRIES AS e
        INNER JOIN PLATES AS p
            ON p.id  = e.plate_id
        INNER JOIN VEHICLE_TYPES AS vt
            ON vt.id = p.vehicle_type_id
        INNER JOIN SPOTS AS s
            ON s.spot_id = e.spot_id
        WHERE e.parking_id = %s AND e.plate_id = %s
        ORDER BY e.created_at DESC
        LIMIT 1
        """

        try:
            cursor.execute(query, (parking_id, plate_id))
            result = cursor.fetchone()

            if not result:
                return "No se encontró un ingreso para esta placa", None

            return None, EntryResponse(
                id=result[0],
                plate=result[1],
                vehicle_type=result[2],
                spot_id=result[3],
                spot=result[4],
                created_at=result[5]
            )

        except Exception as e:
            logger.error("Error en find_latest_entry: %s", e, exc_info=True)
            return "Error al buscar el último ingreso", None

        finally:
            cursor.close()

    @staticmethod
    def find_latest_entry_spot(parking_id: int, plate_id: int, connection):
        cursor = connection.cursor()

        query = """
        SELECT spot_id FROM ENTRIES
        WHERE parking_id = %s AND plate_id = %s
        ORDER BY created_at DESC
        LIMIT 1
        """

        try:
            cursor.execute(query, (parking_id, plate_id))
            result = cursor.fetchone()

            if not result:
                return "No se encontró un ingreso para esta placa", None

            return None, result[0]

        except Exception as e:
            logger.error(
                "Error en find_latest_entry_spot: %s",
                e,
                exc_info=True
            )
            return "Error al buscar el ingreso más reciente", None

        finally:
            cursor.close()

    @staticmethod
    def create_entry(parking_id: int, plate_id: int, spot_id: int, connection):
        cursor = connection.cursor()

        query = """
        INSERT INTO ENTRIES (parking_id, plate_id, spot_id)
        VALUES (%s, %s, %s)
        """

        try:
            cursor.execute(query, (parking_id, plate_id, spot_id))
            return None, True, "Ingreso registrado correctamente"

        except Exception as e:
            logger.error("Error en create_entry: %s", e, exc_info=True)
            return "Error al intentar registrar el ingreso", False, None

        finally:
            cursor.close()
