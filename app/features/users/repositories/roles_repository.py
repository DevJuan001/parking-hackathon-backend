from app.features.users.models.roles_responses import RoleResponse
from app.utils.logger import get_logger

logger = get_logger("roles.repository")


class RolesRepository:
    @staticmethod
    def find_all_roles(connection):
        cursor = connection.cursor()

        query = "SELECT id, name FROM ROLES"

        try:
            cursor.execute(query)
            result = cursor.fetchall()

            data = [
                RoleResponse(
                    id=item[0],
                    name=item[1]
                )
                for item in result
            ]
            return None, data

        except Exception:
            logger.exception("Error en find_all_roles")
            return "Error al intentar obtener los roles", None

        finally:
            cursor.close()
