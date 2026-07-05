import bcrypt
from typing import Optional
from app.utils.logger import get_logger
from app.utils.date_formatter import date_formatter
from app.features.users.models.users_schemas import CompleteUserOnboardingSchema, CreateUserSchema, UpdateUserSchema, UsersFiltersSchema
from app.features.users.models.users_responses import SurnameResponse, UserByEmailResponse, UserByIdResponse, UserResponse, UserStatsResponse

logger = get_logger("users.repository")


class UsersRepository:

    # Obtener todos los usuarios
    @staticmethod
    def find_all_users(parking_id: int, filters_data: UsersFiltersSchema, connection):
        data = filters_data.model_dump(exclude_none=True)

        cursor = connection.cursor()

        # Petición a la base de datos
        query = """
        SELECT
            r.id,
            r.name,
            u.id,
            u.name,
            u.first_surname,
            u.second_surname,
            u.email,
            u.created_at,
            u.status
        FROM USERS AS u
        INNER JOIN ROLES AS r
            ON r.id = u.role_id
        """

        filters = ["u.parking_id = %s"]
        values = [parking_id]

        if "role_order" in data:
            filters.append("r.id = %s")
            values.append(data["role_order"])

        if "first_surname" in data:
            filters.append("u.first_surname = %s")
            values.append(data["first_surname"])

        if "start_date" in data:
            filters.append("DATE(u.created_at) >= %s")
            values.append(data["start_date"])

        if "end_date" in data:
            filters.append("DATE(u.created_at) <= %s")
            values.append(data["end_date"])

        query += " WHERE " + " AND ".join(filters)

        if data.get("name_order") == "asc":
            query += " ORDER BY u.name ASC"
        elif data.get("name_order") == "desc":
            query += " ORDER BY u.name DESC"

        try:
            cursor.execute(query, values)

            results = cursor.fetchall()

            users = [
                UserResponse(
                    role_id=item[0],
                    role_name=item[1],
                    id=item[2],
                    name=item[3],
                    first_surname=item[4],
                    second_surname=item[5],
                    email=item[6],
                    created_at=date_formatter(item[7]),
                    status=item[8]
                )
                for item in results
            ]
            return None, users

        except Exception as e:
            logger.error("Error en find_all_users: %s", e, exc_info=True)
            return "Error al intentar obtener todos los usuarios", None

        finally:
            cursor.close()

    # Obtener los apellidos (first_surname) distintos de los usuarios del parking
    @staticmethod
    def find_all_surnames(parking_id: int, connection):
        cursor = connection.cursor()

        query = """
        SELECT DISTINCT first_surname
        FROM USERS
        WHERE parking_id = %s
        ORDER BY first_surname ASC
        """

        try:
            cursor.execute(query, (parking_id,))

            results = cursor.fetchall()

            surnames = [
                SurnameResponse(surname=item[0])
                for item in results
            ]
            return None, surnames

        except Exception as e:
            logger.error("Error en find_all_surnames: %s", e, exc_info=True)
            return "Error al intentar obtener los apellidos de los usuarios", None

        finally:
            cursor.close()

    # Obtener estadisticas de usuarios del parking
    @staticmethod
    def count_user_stats(parking_id: int, connection):
        cursor = connection.cursor()

        query = """
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN u.status = 2 THEN 1 ELSE 0 END) AS active,
            SUM(CASE WHEN u.status = 1 THEN 1 ELSE 0 END) AS disabled,
            SUM(
                CASE WHEN u.created_at >= (NOW() - INTERVAL 7 DAY) THEN 1
                ELSE 0 END
            ) AS created_this_week
        FROM USERS AS u
        WHERE u.parking_id = %s
        """

        try:
            cursor.execute(query, (parking_id,))
            result = cursor.fetchone()

            stats = UserStatsResponse(
                total=int(result[0] or 0),
                active=int(result[1] or 0),
                disabled=int(result[2] or 0),
                created_this_week=int(result[3] or 0)
            )
            return None, stats

        except Exception as e:
            logger.error("Error en count_user_stats: %s", e, exc_info=True)
            return "Error al intentar obtener las estadisticas de usuarios", None

        finally:
            cursor.close()

    # Obtener un usuario por el ID
    @staticmethod
    def find_user_by_id(parking_id: int, user_id: int, connection):
        cursor = connection.cursor()

        # Petición a la base de datos
        query = """
        SELECT
            r.name,
            u.id,
            u.name,
            u.first_surname,
            u.second_surname,
            u.email,
            u.created_at,
            u.status
        FROM USERS AS u
        INNER JOIN ROLES AS r
            ON r.id = u.role_id
        WHERE u.parking_id = %s AND u.id = %s
        """

        try:
            cursor.execute(query, (parking_id, user_id))

            result = cursor.fetchall()

            if not result:
                return "Usuario no encontrado", None

            data = [
                UserByIdResponse(
                    role=item[0],
                    id=item[1],
                    name=item[2],
                    first_surname=item[3],
                    second_surname=item[4],
                    email=item[5],
                    created_at=date_formatter(item[6]),
                    status=item[7]
                )
                for item in result
            ]
            return None, data[0]

        except Exception as e:
            logger.error("Error en find_user_by_id: %s", e, exc_info=True)
            return "Error al intentar obtener el usuario mediante el id", None

        finally:
            cursor.close()

    # Obtener un usuario por su ID unicamente (no requiere parking_id).
    # Util cuando el usuario todavia no completo el onboarding y su
    # parking_id es NULL.
    @staticmethod
    def find_user_by_id_global(user_id: int, connection):
        cursor = connection.cursor()

        query = """
        SELECT
            r.name,
            u.id,
            u.name,
            u.first_surname,
            u.second_surname,
            u.email,
            u.created_at,
            u.status
        FROM USERS AS u
        INNER JOIN ROLES AS r
            ON r.id = u.role_id
        WHERE u.id = %s
        """

        try:
            cursor.execute(query, (user_id,))

            result = cursor.fetchall()

            if not result:
                return "Usuario no encontrado", None

            data = [
                UserByIdResponse(
                    role=item[0],
                    id=item[1],
                    name=item[2],
                    first_surname=item[3],
                    second_surname=item[4],
                    email=item[5],
                    created_at=date_formatter(item[6]),
                    status=item[7]
                )
                for item in result
            ]
            return None, data

        except Exception as e:
            logger.error(
                "Error en find_user_by_id_global: %s", e, exc_info=True
            )
            return "Error al intentar obtener el usuario mediante el id", None

        finally:
            cursor.close()

    @staticmethod
    def find_user_password_by_id(parking_id: int, user_id: int, connection):
        cursor = connection.cursor()

        # Petición a la base de datos
        query = """
        SELECT
            password
        FROM USERS
        WHERE parking_id = %s AND id = %s
        """

        try:
            cursor.execute(query, (parking_id, user_id))
            result = cursor.fetchone()

            if not result:
                return "Usuario no encontrado", None

            return None, result

        except Exception as e:
            logger.error(
                "Error en find_user_password_by_id: %s",
                e,
                exc_info=True
            )
            return "Error al intentar obtener la contraseña del usuario", None

        finally:
            cursor.close()

    # Obtener un usuario mediante el correo
    @staticmethod
    def find_user_by_email(email: str, connection):
        cursor = connection.cursor(buffered=True)

        # Petición a la base de datos
        query = """
        SELECT
            r.name,
            u.id,
            u.name,
            u.first_surname,
            u.second_surname,
            u.email,
            u.password
        FROM USERS AS u
        INNER JOIN ROLES AS r
            ON r.id = u.role_id
        WHERE u.email = %s
        """

        try:
            cursor.execute(query, (email,))

            result = cursor.fetchall()

            data = [
                UserByEmailResponse(
                    role=item[0],
                    parking_id=item[1],
                    id=item[2],
                    name=item[3],
                    first_surname=item[4],
                    second_surname=item[5],
                    email=item[6],
                    password=item[7],
                )

                for item in result
            ]

            return None, data[0]

        except Exception as e:
            logger.error("Error en find_user_by_email: %s", e, exc_info=True)
            return "Error al intentar obtener el usuario mediante el correo", None

        finally:
            cursor.close()

    # Crear un usuario
    @staticmethod
    def create_user(user_data: CreateUserSchema, hash_password: str, parking_id: Optional[int], connection):
        data = user_data.model_dump()

        cursor = connection.cursor()

        # Petición a la base de datos
        query = """INSERT INTO USERS (
            role_id,
            parking_id,
            name,
            first_surname,
            second_surname,
            password,
            email
        ) VALUES(%s, %s, %s, %s, %s, %s, %s)"""

        try:
            cursor.execute(query, (
                data["role_id"],
                parking_id,
                data["name"],
                data["first_surname"],
                data["second_surname"],
                hash_password,
                data["email"])
            )

            return None, True, "Usuario creado correctamente"

        except Exception as e:
            logger.error("Error en create_user: %s", e, exc_info=True)
            return "Error al intentar crear el usuario", False, None

        finally:
            cursor.close()

    # Completar el onboarding de un usuario (datos personales + parking + flag)
    @staticmethod
    def complete_user_onboarding(
        user_id: int,
        parking_id: int,
        user_data: CompleteUserOnboardingSchema,
        connection
    ):
        cursor = connection.cursor()

        query = """
        UPDATE USERS
        SET parking_id = %s,
            name = %s,
            first_surname = %s,
            second_surname = %s,
            onboarding_completed = 1
        WHERE id = %s
        """

        try:
            cursor.execute(
                query,
                (
                    parking_id,
                    user_data.name,
                    user_data.first_surname,
                    (user_data.second_surname or "").strip(),
                    user_id
                )
            )

            return None, True, "Onboarding completado correctamente"

        except Exception as e:
            logger.error(
                "Error en complete_user_onboarding: %s", e, exc_info=True
            )
            return "Error al intentar completar el onboarding", False, None

        finally:
            cursor.close()

    # Actualizar la información de un usuario
    @staticmethod
    def update_user(parking_id: int, user_id: int, user_data: UpdateUserSchema, connection):
        data = user_data.model_dump(exclude_none=True)

        USER_FIELDS = {
            "role_id": "role_id",
            "name": "name",
            "first_surname": "first_surname",
            "second_surname": "second_surname",
            "email": "email",
            "status": "status"
        }

        cursor = connection.cursor()

        try:
            user_fields = {
                key: data[key]
                for key in USER_FIELDS.keys()
                if key in data
            }

            if user_fields:
                mapped = {
                    USER_FIELDS[key]: value for key, value in user_fields.items()}

                columns = ", ".join(f"{col} = %s" for col in mapped.keys())
                values = list(mapped.values()) + [parking_id, user_id]

                cursor.execute(
                    f"UPDATE USERS SET {columns} WHERE parking_id = %s AND id = %s",
                    values
                )

            return None, True, "Usuario actualizado correctamente"

        except Exception as e:
            logger.error("Error en update_user: %s", e, exc_info=True)
            return "Error al intentar actualizar el usuario", False, None

        finally:
            cursor.close()

    @staticmethod
    def update_user_password(parking_id: int, user_id: int, password: str, connection):
        cursor = connection.cursor()

        query = """
        UPDATE USERS SET
            password = %s
        WHERE parking_id = %s AND id = %s
        """
        new_password = password.encode("utf-8")
        hash_password = bcrypt.hashpw(
            new_password, bcrypt.gensalt(rounds=12)).decode("utf-8")

        try:
            cursor.execute(query, (hash_password, parking_id, user_id))

            return None, True, "Contraseña actualizada correctamente"

        except Exception:
            return "Error al intentar actualizar la contraseña del usuario", False, None

        finally:
            cursor.close()

    # Deshabilitar un usuario
    @staticmethod
    def disable_user(parking_id: int, user_id: int, connection):
        cursor = connection.cursor()

        query = "UPDATE USERS SET status = 1 WHERE parking_id = %s AND id = %s"

        try:
            cursor.execute(query, (parking_id, user_id))
            return None, True, "Usuario deshabilitado correctamente"

        except Exception as e:
            logger.error("Error en disable_user: %s", e, exc_info=True)
            return "Error la intentar deshabilitar el usuario", False, None

        finally:
            cursor.close()

    # Habilitar un usuario
    @staticmethod
    def enable_user(parking_id: int, user_id: int, connection):
        cursor = connection.cursor()

        query = "UPDATE USERS SET status = 2 WHERE parking_id = %s AND id = %s"

        try:
            cursor.execute(query, (parking_id, user_id))

            return None, True, "Usuario habilitado correctamente"

        except Exception as e:
            logger.error("Error en enable_user: %s", e, exc_info=True)
            return "Error la intentar habilitar el usuario", False, None

        finally:
            cursor.close()
