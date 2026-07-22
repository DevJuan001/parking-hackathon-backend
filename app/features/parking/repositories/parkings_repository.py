from app.utils.logger import get_logger

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
    def update_parking(parking_id: int, connection, name=None, address=None, phone=None):
        cursor = connection.cursor()

        fields = {}

        if name is not None:
            fields["name"] = name.strip()

        if address is not None:
            fields["address"] = address.strip()

        if phone is not None:
            fields["phone"] = phone.strip()

        if not fields:
            return None, True

        set_clause = ", ".join(f"{k} = %s" for k in fields)

        values = list(fields.values())

        values.append(parking_id)

        query = f"UPDATE PARKINGS SET {set_clause} WHERE id = %s"

        try:
            cursor.execute(query, tuple(values))

            return None, cursor.rowcount > 0

        except Exception as e:
            logger.error("Error en update_parking: %s", e, exc_info=True)
            return "Error al intentar actualizar el parking", False

        finally:
            cursor.close()
