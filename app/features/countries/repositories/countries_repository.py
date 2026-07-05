from app.utils.logger import get_logger
from app.features.countries.models.countries_responses import CountryResponse

logger = get_logger("countries.repository")


class CountriesRepository:

    @staticmethod
    def find_all_countries(connection):
        cursor = connection.cursor()

        query = """
        SELECT id, name, iso_code
        FROM COUNTRIES
        ORDER BY name ASC
        """

        try:
            cursor.execute(query)
            results = cursor.fetchall()

            countries = [
                CountryResponse(
                    id=item[0],
                    name=item[1],
                    iso_code=item[2]
                )
                for item in results
            ]
            return None, countries

        except Exception as e:
            logger.error(
                "Error en find_all_countries: %s", e, exc_info=True
            )
            return "Error al intentar obtener los paises", None

        finally:
            cursor.close()
