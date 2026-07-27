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
                    name=item[1],
                    level=item[2],
                    start_date=item[3],
                    end_date=item[4],
                    created_at=item[5],
                    status=item[6],
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
