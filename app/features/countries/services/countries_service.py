from app.utils.logger import get_logger
from app.core.exception import ServiceError
from app.core.database import get_connection
from app.features.countries.repositories.countries_repository import CountriesRepository

logger = get_logger("countries.service")


class CountriesService:

    @staticmethod
    def get_all_countries():
        connection = get_connection()

        try:
            error, countries = CountriesRepository.find_all_countries(
                connection
            )

            if error:
                raise ServiceError(error)

            return None, countries

        except ServiceError as e:
            return e.message, None

        except Exception as e:
            logger.error(
                "Error en get_all_countries: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener los paises", None

        finally:
            connection.close()
