from pydantic import EmailStr
from app.utils.logger import get_logger
from app.features.reservations.models.reservations_responses import ReservationsResponse
from app.features.reservations.models.reservations_schemas import FilterReservationsSchema, UpdateReservationSchema

logger = get_logger("reservations.repository")


class ReservationsRepository():
    @staticmethod
    def find_all_reservations(filters_data: FilterReservationsSchema, parking_id: str, connection):
        cursor = connection.cursor()

        data = filters_data.model_dump(exclude_none=True)

        query = """
        SELECT
            uuid,
            name,
            email,
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
            filters.append("DATE(start_date) >= %s")
            values.append(data["start_date"])

        if "end_date" in data:
            filters.append("(end_date IS NULL OR DATE(end_date) <= %s)")
            values.append(data["end_date"])

        if filters:
            query += " WHERE " + " AND ".join(filters)

        query += " ORDER BY start_date LIMIT %s OFFSET %s"

        per_page = filters_data.per_page
        offset = (filters_data.page - 1) * per_page
        values += [per_page, offset]

        try:
            cursor.execute(query, values)

            results = cursor.fetchall()

            data = [
                ReservationsResponse(
                    uuid=item[0],
                    name=item[1],
                    email=item[2],
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
    def find_reservation_by_id(reservation_id: str, parking_id: str, connection):
        cursor = connection.cursor()

        query = """
        SELECT
            uuid,
            name,
            email,
            level,
            start_date,
            end_date,
            created_at,
            status
        FROM RESERVATIONS
        WHERE uuid = %s AND parking_id = %s
        """

        try:
            cursor.execute(query, (reservation_id, parking_id))

            result = cursor.fetchone()

            return None, ReservationsResponse(
                uuid=result[0],
                name=result[1],
                email=result[2],
                level=result[3],
                start_date=result[4].date(),
                start_time=result[4].time(),
                end_date=result[5].date() if result[5] else None,
                end_time=result[5].time() if result[5] else None,
                created_at=result[6],
                status=result[7],
            )

        except Exception as e:
            logger.error(
                "Error en find_reservation_by_id: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener la reserva", None

        finally:
            cursor.close()

    @staticmethod
    def create_reservation(
        parking_id: str,
        uuid: str,
        name: str,
        email: EmailStr,
        plate: str,
        level: int,
        start_datetime,
        end_datetime,
        connection,
    ):
        cursor = connection.cursor()

        query = """
        INSERT INTO RESERVATIONS (
            uuid,
            parking_id,
            name,
            email,
            plate,
            level,
            start_date,
            end_date
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        try:
            cursor.execute(
                query, (
                    uuid,
                    parking_id,
                    name,
                    email,
                    plate,
                    level,
                    start_datetime,
                    end_datetime
                ),
            )

            reservation_id = cursor.lastrowid

            return None, True, "Reserva creada correctamente", reservation_id

        except Exception as e:
            logger.error(
                "Error en create_reservation: %s",
                e,
                exc_info=True
            )
            return "Error al intentar crear la reserva", False, None, None

        finally:
            cursor.close()

    @staticmethod
    def update_reservation(reservation_id: str, parking_id: str, reservation_data: UpdateReservationSchema, connection):
        data = reservation_data.model_dump(exclude_none=True)

        cursor = connection.cursor()

        RESERVATION_FIELDS = {
            "name": "name",
            "level": "level",
            "user_id": "user_id",
            "start_date": "start_date",
            "end_date": "end_date",
            "status": "status"
        }

        try:
            reservations_fields = {
                key: data[key]
                for key in RESERVATION_FIELDS.keys()
                if key in data
            }

            if reservations_fields:
                mapped = {
                    RESERVATION_FIELDS[key]: value for key, value in reservations_fields.items()}

                columns = ", ".join(f"{col} = %s" for col in mapped.keys())
                values = list(mapped.values()) + [parking_id, reservation_id]

                cursor.execute(
                    f"UPDATE RESERVATIONS SET {columns} WHERE parking_id = %s AND uuid = %s",
                    values
                )

            return None, True, "Reserva actualizada correctamente"

        except Exception as e:
            logger.error(
                "Error en update_reservation_status: %s",
                e,
                exc_info=True
            )
            return "Error al intentar actualizar la reserva", False, None

        finally:
            cursor.close()

    @staticmethod
    def delete_reservation(reservation_id: str, parking_id: str, connection):
        cursor = connection.cursor()

        query = """
        DELETE FROM RESERVATIONS
        WHERE uuid = %s AND parking_id = %s
        """

        try:
            cursor.execute(query, (reservation_id, parking_id))

            if cursor.rowcount == 0:
                return "Reserva no encontrada", False, None

            return None, True, "Reserva eliminada correctamente"

        except Exception as e:
            logger.error(
                "Error en delete_reservation: %s",
                e,
                exc_info=True
            )
            return "Error al intentar eliminar la reserva", False, None

        finally:
            cursor.close()
