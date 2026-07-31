from app.utils.logger import get_logger
from app.features.reservations.models.reservations_responses import ReservationsResponse
from app.features.reservations.models.reservations_schema import FilterReservationsSchema

logger = get_logger("reservations.repository")


class ReservationsRepository():
    @staticmethod
    def find_all_reservations(filters_data: FilterReservationsSchema, parking_id: int, connection):
        cursor = connection.cursor()

        data = filters_data.model_dump(exclude_none=True)

        query = """
        SELECT
            id,
            user_id,
            name,
            level,
            start_date,
            end_date,
            created_at,
            status
        FROM RESERVATIONS
        """

        filters = ["parking_id = %s"]
        values = [parking_id]

        if "start_date" in data:
            filters.append("DATE(created_at) >= %s")
            values.append(data["start_date"])

        if "end_date" in data:
            filters.append("DATE(created_at) <= %s")
            values.append(data["end_date"])

        if filters:
            query += " WHERE " + " AND ".join(filters)

        try:
            cursor.execute(query, values)

            results = cursor.fetchall()

            data = [
                ReservationsResponse(
                    id=item[0],
                    user_id=item[1],
                    name=item[2],
                    level=item[3],
                    start_date=item[4].date(),
                    start_time=item[4].time(),
                    end_date=item[5].date() if item[5] else None,
                    end_time=item[5].time() if item[5] else None,
                    created_at=item[6],
                    status=item[7],
                )

                for item in results
            ]

            return None, data

        except Exception as e:
            logger.error(
                "Error en find_all_reservations: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener las reservas", None

        finally:
            cursor.close()

    @staticmethod
    def create_reservation(
        parking_id: int,
        user_id: int,
        name: str,
        level: int,
        start_datetime,
        end_datetime,
        connection,
    ):
        cursor = connection.cursor()

        query = """
        INSERT INTO RESERVATIONS (
            parking_id,
            user_id,
            name,
            level,
            start_date,
            end_date
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        try:
            cursor.execute(
                query,
                (parking_id, user_id, name, level, start_datetime, end_datetime),
            )

            return None, True, "Reserva creada correctamente"

        except Exception as e:
            logger.error(
                "Error en create_reservation: %s",
                e,
                exc_info=True
            )
            return "Error al intentar crear la reserva", False, None

        finally:
            cursor.close()
