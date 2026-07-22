import mysql.connector
from mysql.connector import Error
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger("database")


# Función para conectar a la base de datos
def get_connection():
    try:
        connection = mysql.connector.connect(
            host=settings.DB_HOST or "localhost",
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci"
        )

        return connection

    except Error as e:
        logger.error(
            "Error al intentar conectar con la base de datos: %s",
            e,
            exc_info=True
        )

        return None


get_connection()
