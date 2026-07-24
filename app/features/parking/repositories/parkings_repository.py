from app.utils.logger import get_logger
from app.features.parking.models.parking_schemas import UpdateParkingSchema

logger = get_logger("parkings.repository")


class ParkingsRepository:

    @staticmethod
    def create_parking(name: str, country_id: int, connection):
        cursor = connection.cursor()

        query = """
        INSERT INTO PARKINGS (name, country_id)
        VALUES (%s, %s)
        """

        try:
            cursor.execute(query, (name, country_id))
            return None, True, cursor.lastrowid

        except Exception as e:
            logger.error("Error en create_parking: %s", e, exc_info=True)
            return "Error al intentar crear el parking", False, None

        finally:
            cursor.close()

    @staticmethod
    def update_parking(
        parking_id: int,
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
