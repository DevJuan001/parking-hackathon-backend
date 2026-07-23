from app.utils.logger import get_logger

logger = get_logger("chatbot.repository")


class ChatbotRepository:

    @staticmethod
    def get_parking_info(parking_id: int, connection):
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT 
            p.id, 
            p.name,
            p.country_id,
            c.name,
            p.created_at
        FROM PARKINGS AS p
        INNER JOIN COUNTRIES AS c
            ON p.country_id = c.id
        WHERE p.id = %s
        """

        try:
            cursor.execute(query, (parking_id,))
            return None, cursor.fetchone()

        except Exception as e:
            logger.error("Error en get_parking_info: %s", e, exc_info=True)
            return "Error al intentar obtener la información del parking", None

        finally:
            cursor.close()

    @staticmethod
    def get_tariffs_with_vehicle_type(parking_id: int, connection):
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT
            t.id,
            vt.name AS vehicle_type,
            t.value
        FROM RATES AS t
        JOIN VEHICLE_TYPES AS vt
            ON vt.id = t.vehicle_type_id
        WHERE t.parking_id = %s
        """

        try:
            cursor.execute(query, (parking_id,))
            return None, cursor.fetchall()

        except Exception as e:
            logger.error(
                "Error en get_tariffs_with_vehicle_type: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener las tarifas", None

        finally:
            cursor.close()

    @staticmethod
    def get_occupancy_stats(parking_id: int, connection):
        cursor = connection.cursor(dictionary=True)

        try:
            stats = {}

            for key, status in (("total", None), ("occupied", 3), ("free", 2)):
                if status is None:
                    cursor.execute(
                        """
                        SELECT
                            COUNT(*) AS count
                        FROM SPOTS AS s 
                        JOIN FLOORS AS f 
                            ON f.id = s.floor_id
                        WHERE f.parking_id = %s""",
                        (parking_id,),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT
                            COUNT(*) AS count
                        FROM SPOTS AS s
                        JOIN FLOORS AS f
                            ON f.id = s.floor_id
                        WHERE f.parking_id = %s AND s.spot_status = %s""",
                        (parking_id, status),
                    )

                stats[key] = cursor.fetchone()["count"]

            return None, stats

        except Exception as e:
            logger.error("Error en get_occupancy_stats: %s", e, exc_info=True)
            return "Error al intentar obtener las estadísticas de ocupación", None

        finally:
            cursor.close()

    @staticmethod
    def get_daily_summary(parking_id: int, connection):
        from datetime import date

        cursor = connection.cursor(dictionary=True)
        today = date.today()

        try:
            cursor.execute(
                """
                SELECT
                    COUNT(*) AS total_entries
                FROM ENTRIES
                WHERE parking_id = %s AND DATE(created_at) = %s""",
                (parking_id, today),
            )

            entries_count = cursor.fetchone()["total_entries"]

            cursor.execute(
                """
                SELECT
                    COUNT(*) AS total_exits,
                    COALESCE(SUM(value), 0) AS total_revenue
                FROM PAYMENTS
                WHERE parking_id = %s AND DATE(created_at) = %s""",
                (parking_id, today),
            )

            row = cursor.fetchone()

            return None, {
                "date": today.isoformat(),
                "entries_today": entries_count,
                "exits_today": row["total_exits"],
                "revenue_today": float(row["total_revenue"]),
            }

        except Exception as e:
            logger.error("Error en get_daily_summary: %s", e, exc_info=True)
            return "Error al intentar obtener el resumen del día", None

        finally:
            cursor.close()

    @staticmethod
    def get_all_payment_methods(connection):
        cursor = connection.cursor(dictionary=True)

        query = "SELECT id, name FROM PAYMENT_METHODS"

        try:
            cursor.execute(query)
            return None, cursor.fetchall()

        except Exception as e:
            logger.error(
                "Error en get_all_payment_methods: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener los métodos de pago", None

        finally:
            cursor.close()

    @staticmethod
    def get_snapshot_data(parking_id: int, connection):
        cursor = connection.cursor()

        data = {}

        queries = {
            "parking_name": (
                """
                SELECT
                    name
                FROM PARKINGS
                WHERE id = %s""",
                (parking_id,),
            ),
            "total_floors": (
                """
                SELECT
                    COUNT(1)
                FROM FLOORS
                WHERE parking_id = %s""",
                (parking_id,),
            ),
            "total_spots": (
                """
                SELECT
                    COUNT(1)
                FROM SPOTS AS s
                JOIN FLOORS AS f
                    ON f.id = s.floor_id
                WHERE f.parking_id = %s""",
                (parking_id,),
            ),
            "occupied_spots": (
                """
                SELECT
                    COUNT(1)
                FROM SPOTS AS s
                JOIN FLOORS AS f
                    ON f.id = s.floor_id
                WHERE f.parking_id = %s AND s.spot_status = 3""",
                (parking_id,),
            ),
            "active_entries": (
                """
                SELECT COUNT(1) FROM ENTRIES e
                WHERE e.parking_id = %s
                AND NOT EXISTS (
                    SELECT 1 FROM EXITS x
                    WHERE x.parking_id = e.parking_id
                    AND x.plate_id = e.plate_id
                    AND x.created_at > e.created_at
                )
                """,
                (parking_id,),
            ),
            "today_payments": (
                """SELECT
                    COUNT(1), 
                    COALESCE(SUM(value), 0) 
                FROM PAYMENTS
                WHERE parking_id = %s AND DATE(created_at) = CURDATE()""",
                (parking_id,),
            ),
        }

        for key, (query, params) in queries.items():
            try:
                cursor.execute(query, params)
                row = cursor.fetchone()

                if key == "today_payments":
                    data[key] = (row[0], row[1]) if row else (0, 0)
                else:
                    data[key] = row[0] if row else None

            except Exception as e:
                logger.warning("No se pudo obtener %s: %s", key, e)
                data[key] = None

        try:
            cursor.execute(
                """
                SELECT
                    f.name,
                    JSON_ARRAYAGG(s.spot)
                FROM FLOORS AS f
                JOIN SPOTS AS s
                    ON s.floor_id = f.id
                WHERE f.parking_id = %s
                GROUP BY f.id, f.name
                ORDER BY f.name
                """,
                (parking_id,),
            )
            data["floors_with_spots"] = cursor.fetchall()
        
        except Exception as e:
            logger.warning("No se pudo obtener floors_with_spots: %s", e)
            data["floors_with_spots"] = None

        try:
            cursor.execute(
                """
                SELECT
                    vt.name,
                    t.value
                FROM RATES AS t
                JOIN VEHICLE_TYPES AS vt
                    ON vt.id = t.vehicle_type_id
                WHERE t.parking_id = %s
                """,
                (parking_id,),
            )
            data["tariffs"] = cursor.fetchall()
        
        except Exception as e:
            logger.warning("No se pudo obtener tarifas: %s", e)
            data["tariffs"] = None

        cursor.close()

        return None, data
