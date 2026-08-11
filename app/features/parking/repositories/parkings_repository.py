from app.features.parking.models.parking_responses import ParkingPrivateResponse, ParkingResponse
from app.utils.logger import get_logger
from app.features.parking.models.parking_schemas import UpdateParkingSchema

logger = get_logger("parkings.repository")


class ParkingsRepository:

    @staticmethod
    def find_parking_by_private_info(parking_id: str, connection):
        cursor = connection.cursor()

        query = """
        SELECT
            p.uuid,
            p.name,
            c.name,
            pl.name,
            pl.value,
            s.next_payment_at
        FROM PARKINGS AS p
        INNER JOIN COUNTRIES AS c
            ON p.country_id = c.id
        INNER JOIN PLANS AS pl
            ON p.plan_id = pl.id
        INNER JOIN SUSCRIPTIONS AS s
            ON s.parking_id = p.uuid 
        WHERE p.uuid = %s
        """

        try:
            cursor.execute(query, (parking_id,))

            result = cursor.fetchone()

            return None, ParkingPrivateResponse(
                uuid=result[0],
                name=result[1],
                country=result[2],
                plan=result[3],
                plan_value=result[4],
                next_payment_at=result[5].date(),
            )

        except Exception as e:
            logger.error(
                "Error en find_parking_by_private_info: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener la información del parking", None

        finally:
            cursor.close()

    @staticmethod
    def find_parking_by_id(parking_id: str, connection):
        cursor = connection.cursor()

        query = """
        SELECT
            p.uuid,
            p.name,
            c.name
        FROM PARKINGS AS p
        INNER JOIN COUNTRIES AS c
            ON p.country_id = c.id
        WHERE p.uuid = %s
        """

        try:
            cursor.execute(query, (parking_id,))

            result = cursor.fetchone()

            return None, ParkingResponse(
                uuid=result[0],
                name=result[1],
                country=result[2]
            )

        except Exception as e:
            logger.error("Error en find_parking_by_id: %s", e, exc_info=True)
            return "Error al intentar obtener la información del parking", None

        finally:
            cursor.close()

    @staticmethod
    def create_parking(uuid: str, plan_id: int, name: str, country_id: int, connection):
        cursor = connection.cursor()

        query = """
        INSERT INTO PARKINGS (uuid, plan_id, name, country_id)
        VALUES (%s, %s, %s, %s)
        """

        try:
            cursor.execute(query, (uuid, plan_id, name, country_id))

            return None, True, uuid

        except Exception as e:
            logger.error("Error en create_parking: %s", e, exc_info=True)

            return "Error al intentar crear el parking", False, None

        finally:
            cursor.close()

    @staticmethod
    def update_parking(
        parking_id: str,
        parking_data: UpdateParkingSchema,
        connection,
    ):
        data = parking_data.model_dump(exclude_none=True)

        PARKING_FIELDS = {"name": "name"}

        cursor = connection.cursor()

        try:
            parking_fields = {
                key: data[key]
                for key in PARKING_FIELDS.keys()
                if key in data
            }

            if parking_fields:
                mapped = {
                    PARKING_FIELDS[k]: v for k, v in parking_fields.items()
                }

                columns = ", ".join(f"{col} = %s" for col in mapped.keys())
                values = list(mapped.values()) + [parking_id]

                cursor.execute(
                    f"UPDATE PARKINGS SET {columns} WHERE id = %s",
                    values,
                )

            return None, True, "Parking actualizado correctamente"

        except Exception as e:
            logger.error("Error en update_parking: %s", e, exc_info=True)
            return "Error al intentar actualizar el parking", False, None

        finally:
            cursor.close()
