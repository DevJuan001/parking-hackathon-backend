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
