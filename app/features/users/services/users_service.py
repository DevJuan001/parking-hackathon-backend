import bcrypt
from pydantic import EmailStr

from app.core.database import get_connection
from app.core.exception import ServiceError
from app.core.security import generate_temporal_password, verify_password
from app.features.users.models.users_schemas import (
    CreateUserSchema,
    UpdatePasswordSchema,
    UpdateUserSchema,
    UsersFiltersSchema,
)
from app.features.users.repositories.roles_repository import RolesRepository
from app.features.users.repositories.users_repository import UsersRepository
from app.tasks.email_tasks import send_welcome_email
from app.utils.logger import get_logger

logger = get_logger("users.service")


class UsersService:
    @staticmethod
    def get_all_users(parking_id: str, filters: UsersFiltersSchema):
        connection = get_connection()

        try:
            error, users = UsersRepository.find_all_users(
                parking_id,
                filters,
                connection
            )

            if error:
                raise ServiceError(error)

            return None, users

        except ServiceError as e:
            return e.message, None

        except Exception:
            logger.exception("Error en get_all_users")
            return "Error al intentar obtener los usuarios", None

        finally:
            connection.close()

    @staticmethod
    def get_user_stats(parking_id: str):
        connection = get_connection()

        try:
            error, stats = UsersRepository.count_user_stats(
                parking_id, connection
            )

            if error:
                raise ServiceError(error)

            return None, stats

        except ServiceError as e:
            return e.message, None

        except Exception:
            logger.exception("Error en get_user_stats")
            return "Error al intentar obtener las estadisticas de usuarios", None

        finally:
            connection.close()

    @staticmethod
    def get_user_by_id(parking_id: str, user_id: int):
        connection = get_connection()

        try:
            error, user = UsersRepository.find_user_by_id(
                parking_id,
                user_id,
                connection
            )

            if error or not user:
                raise ServiceError(error)

            return None, user

        except ServiceError as e:
            return e.message, None

        except Exception:
            logger.exception("Error en get_user_by_id")
            return "Error al intentar obtener el usuario mediante el id", None

        finally:
            connection.close()

    @staticmethod
    def get_user_by_id_global(user_id: int):
        connection = get_connection()

        try:
            error, user = UsersRepository.find_user_by_id_global(
                user_id,
                connection
            )

            if error or not user:
                raise ServiceError(error)

            return None, user

        except ServiceError as e:
            return e.message, None

        except Exception:
            logger.exception("Error en get_user_by_id_global")
            return "Error al intentar obtener el usuario mediante el id", None

        finally:
            connection.close()

    @staticmethod
    def get_user_by_email(email: EmailStr):
        connection = get_connection()

        try:
            error, user = UsersRepository.find_user_by_email(
                email,
                connection
            )

            if error or not user:
                raise ServiceError(error)

            return None, user

        except ServiceError as e:
            return e.message, None

        except Exception:
            logger.exception("Error en get_user_by_email")
            return "Error al intentar obtener el usuario mediante el correo", None

        finally:
            connection.close()

    @staticmethod
    def get_all_roles():
        connection = get_connection()

        try:
            error, roles = RolesRepository.find_all_roles(
                connection
            )

            if error or not roles:
                raise ServiceError(error)

            return None, roles

        except ServiceError as e:
            return e.message, None

        except Exception:
            logger.exception("Error en get_all_roles")
            return "Error al intentar obtener los roles", None

        finally:
            connection.close()

    @staticmethod
    def get_all_surnames(parking_id: str):
        connection = get_connection()

        try:
            error, surnames = UsersRepository.find_all_surnames(
                parking_id,
                connection
            )

            if error:
                raise ServiceError(error)

            return None, surnames

        except ServiceError as e:
            return e.message, None

        except Exception:
            logger.exception("Error en get_all_surnames")
            return "Error al intentar obtener los apellidos de los usuarios", None

        finally:
            connection.close()

    @staticmethod
    async def create_user(user_data: CreateUserSchema, parking_id: int):
        data = user_data.model_dump()

        connection = get_connection()

        try:
            # Verificar que no este registrado ya un usuario con el correo que viene
            error, user = UsersRepository.find_user_by_email(
                email=data["email"],
                connection=connection
            )

            if error:
                raise ServiceError(error)

            if user:
                raise ServiceError(
                    "Este correo ya esta registrado, intenta ingresar otro correo e intentalo nuevamente"
                )

            temporal_password = generate_temporal_password()

            # Hashear la contraseña
            password = temporal_password.encode("utf-8")
            hash_password = bcrypt.hashpw(
                password, bcrypt.gensalt(rounds=12)
            ).decode("utf-8")

            error, success, _message = UsersRepository.create_user(
                user_data=user_data,
                hash_password=hash_password,
                parking_id=parking_id,
                onboarding_completed=True,
                provider="Local",
                connection=connection
            )

            if error or not success:
                raise ServiceError(error)

            connection.commit()

            send_welcome_email.delay(
                user_name=data["name"],
                user_first_surname=data["first_surname"],
                user_email=data["email"],
                password=temporal_password
            )

            return None, True, "Usuario Creado Correctamente"

        except ServiceError as e:
            connection.rollback()
            return e.message, False, None

        except Exception:
            connection.rollback()
            logger.exception("Error en create_user")
            return "Error al intentar crear el usuario", False, None

        finally:
            connection.close()

    @staticmethod
    def update_user(parking_id: str, user_id: int, user_data: UpdateUserSchema):
        data = user_data.model_dump(exclude_none=True)
        connection = get_connection()

        try:
            # Verificar si existe el usuario
            error, user = UsersRepository.find_user_by_id(
                parking_id, user_id, connection
            )

            if not user:
                raise ServiceError(error)

            # Verificar si el correo ya esta siendo usado y no duplicarlo
            if "email" in data:
                error, existing_user = UsersRepository.find_user_by_email(
                    data["email"], connection
                )

                if existing_user and (existing_user.id != user_id):
                    raise ServiceError(
                        "El correo ya está registrado, ingresa un correo diferente e intentalo nuevamente"
                    )

            error, success, _message = UsersRepository.update_user(
                parking_id, user_id, user_data, connection
            )

            if error or not success:
                raise ServiceError(error)

            connection.commit()

            return None, True, "Usuario Actualizado Correctamente"

        except ServiceError as e:
            connection.rollback()
            return e.message, False, None

        except Exception:
            connection.rollback()
            logger.exception("Error en update_user")
            return "Error al intentar actualizar el usuario", False, None

        finally:
            connection.close()

    @staticmethod
    def update_user_password(parking_id: str, password_data: UpdatePasswordSchema, user_id: int):
        data = password_data.model_dump()

        connection = get_connection()

        try:
            if data["new_password"] != data["repeat_password"]:
                raise ServiceError("Las contraseñas no coiniciden")

            # Buscamos la contraseña del usuario con ese id
            error, user = UsersRepository.find_user_password_by_id(
                parking_id, user_id, connection
            )

            if error or not user:
                raise ServiceError(error)

            # Validamos que la contraseña antigua sea igual a la que esta registrada
            success = verify_password(
                str(user[0]), data["old_password"]
            )

            if not success:
                raise ServiceError(
                    "Verifique que su contraseña anterior sea la correcta y vuelva a intentarlo"
                )

            error, success, _message = UsersRepository.update_user_password(
                parking_id, user_id, data["new_password"], connection
            )

            if error or not success:
                raise ServiceError(error)

            connection.commit()

            return None, True, "Contraseña actualizada correctamente"

        except ServiceError as e:
            connection.rollback()
            return e.message, False, None

        except Exception:
            connection.rollback()
            logger.exception("Error en update_user_password")
            return "Error al intentar actualizar la contraseña", False, None

        finally:
            connection.close()

    @staticmethod
    def disable_user(parking_id: str, user_id: int):
        connection = get_connection()

        try:
            # Validar que el usuario exista
            error, user = UsersRepository.find_user_by_id(
                parking_id, user_id, connection
            )

            if error or not user:
                raise ServiceError(error)

            error, success, _message = UsersRepository.disable_user(
                parking_id, user_id, connection
            )

            if error or not success:
                raise ServiceError(error)

            connection.commit()

            return None, True, "Usuario deshabilitado correctamente"

        except ServiceError as e:
            connection.rollback()
            return e.message, False, None

        except Exception:
            connection.rollback()
            logger.exception("Error en disable_user")
            return "Error al intentar deshabilitar el usuario", False, None

        finally:
            connection.close()

    @staticmethod
    def enable_user(parking_id: str, user_id: int):
        connection = get_connection()

        try:
            # Validar que el usuario exista
            error, user = UsersRepository.find_user_by_id(
                parking_id, user_id, connection
            )

            if error or not user:
                raise ServiceError(error)

            error, success, _message = UsersRepository.enable_user(
                parking_id, user_id, connection
            )

            if error or not success:
                raise ServiceError(error)

            connection.commit()

            return None, True, "Usuario habilitado correctamente"

        except ServiceError as e:
            connection.rollback()
            return e.message, False, None

        except Exception:
            connection.rollback()
            logger.exception("Error en enable_user")
            return "Error al intentar habilitar el usuario", False, None

        finally:
            connection.close()
