

import jwt
import bcrypt
from datetime import timedelta
from fastapi import Request, Response
from jwt.exceptions import PyJWTError
from pydantic import EmailStr

from app.core.config import settings
from app.utils.logger import get_logger
from app.core.exception import ServiceError
from app.core.database import get_connection
from app.features.users.services.users_service import UsersService
from app.features.users.repositories.users_repository import UsersRepository
from app.core.token_blacklist import add_to_blacklist, get_token_remaining_ttl
from app.features.floors.repositories.floors_repository import FloorsRepository
from app.features.auth.models.auth_schema import OnboardingSchema, RegisterSchema
from app.features.parking.repositories.parkings_repository import ParkingsRepository
from app.tasks.email_tasks import recovery_password_email, send_welcome_registration_email
from app.features.users.models.users_schemas import CompleteUserOnboardingSchema, CreateUserSchema
from app.core.security import create_access_token, create_refresh_token, set_auth_cookies, verify_password


logger = get_logger("auth.service")


class AuthService:
    @staticmethod
    def login(email: str, password: str, response: Response):
        try:
            connection = get_connection()

            error, user = UsersRepository.find_user_by_email(email, connection)

            if error or not user:
                raise ServiceError(error)

            # Validación de los parametros recibidos
            if not verify_password(user.password, password):
                raise ServiceError("Contraseña incorrecta")

            # Tiempo en que expira el token
            expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)

            # Creación del token
            access_token = create_access_token({
                "sub": str(user.id),
                "role": user.role,
                "parking_id": user.parking_id,
                "onboarding_completed": True,
            },
                expires_delta=expires
            )

            refresh_token = create_refresh_token({
                "sub": str(user.id),
                "role": user.role,
                "parking_id": user.parking_id,
                "onboarding_completed": True,
            })

            set_auth_cookies(response, access_token, refresh_token)

            return None, True, "Inicio de sesión exitoso"

        except ServiceError as e:
            return e.message, False, "No autorizado"

        except Exception as e:
            logger.error("Error en login: %s", e, exc_info=True)
            return "No autorizado", False, None

    @staticmethod
    async def register(data: RegisterSchema, response: Response):
        connection = get_connection()

        try:
            # Verficamos que las contraseñas sean iguales
            if data.password != data.repeat_password:
                raise ServiceError("Las contraseñas no coinciden")

            # Buscamos si ya hay un usuario registrado con ese correo
            error, existing_user = UsersService.get_user_by_email(data.email)

            if error:
                raise ServiceError(error)

            if existing_user:
                raise ServiceError(
                    "Lo sentimos por el momento no podemos crear tu cuenta, por favor intentalo nuevamente más tarde"
                )

            # Hasheamos la contraseña que envia el usuario
            password_bytes = data.password.encode("utf-8")
            hash_password = bcrypt.hashpw(
                password_bytes, bcrypt.gensalt(rounds=12)
            ).decode("utf-8")

            # Creamos un modelo del usuario poniendo strings vacios en los datos que faltan
            shell_user = CreateUserSchema(
                role_id=1,
                name="",
                first_surname="",
                second_surname="",
                email=data.email
            )

            # Creamos el usuario
            error, success, message = UsersRepository.create_user(
                user_data=shell_user,
                hash_password=hash_password,
                parking_id=None,
                connection=connection
            )

            if error or not success:
                raise ServiceError(error or message)

            # Buscamos el usuario que acabamos de crear
            error, new_user = UsersRepository.find_user_by_email(
                email=data.email,
                connection=connection
            )

            if error or not new_user:
                raise ServiceError(
                    error or "No se pudo obtener el usuario creado"
                )

            connection.commit()

            expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)

            # Creamos los tokens de acceso
            access_token = create_access_token(
                {
                    "sub": str(new_user.id),
                    "role": new_user.role,
                    "parking_id": new_user.parking_id,
                    "onboarding_completed": False
                },
                expires_delta=expires
            )

            refresh_token = create_refresh_token({
                "sub": str(new_user.id),
                "role": new_user.role,
                "parking_id": new_user.parking_id,
                "onboarding_completed": False
            })

            set_auth_cookies(response, access_token, refresh_token)

            return None, True, "Registro exitoso"

        except ServiceError as e:
            connection.rollback()
            return e.message, False, None

        except Exception as e:
            connection.rollback()
            logger.error("Error en register: %s", e, exc_info=True)
            return "Error al intentar registrar el usuario", False, None

        finally:
            connection.close()

    @staticmethod
    async def complete_onboarding(
        data: OnboardingSchema,
        payload: dict,
        response: Response
    ):
        connection = get_connection()

        try:
            user_id = int(payload["user_id"])

            if payload.get("onboarding_completed"):
                raise ServiceError("El usuario ya completó el onboarding")

            # Creamos un parking nuevo para ese usuario
            error, parking_id, parking_message = ParkingsRepository.create_parking(
                name=data.parking_name.strip(),
                country_id=data.parking_country,
                connection=connection,
            )

            if error or not parking_id:
                raise ServiceError(error or parking_message)

            # Creamos el piso por defecto del parking para que el admin
            # pueda empezar a registrar plazas sin pasos extra
            error, floor_ok, floor_message = FloorsRepository.create_floor(
                parking_id=parking_id,
                name="Piso 1",
                connection=connection,
            )

            if error or not floor_ok:
                raise ServiceError(
                    error or floor_message or "No se pudo crear el piso por defecto"
                )

            # Actualizamos los datos del usuario y le asignamos el parking que recien creamos
            user_data = CompleteUserOnboardingSchema(
                name=data.name,
                first_surname=data.first_surname,
                second_surname=data.second_surname
            )

            error, success, message = UsersRepository.complete_user_onboarding(
                user_id=user_id,
                parking_id=parking_id,
                user_data=user_data,
                connection=connection
            )

            if error or not success:
                raise ServiceError(error or message)

            # Buscamos al usuario mediante el id
            error, user = UsersRepository.find_user_by_id(
                parking_id=parking_id,
                user_id=user_id,
                connection=connection
            )

            if error or not user:
                raise ServiceError(error or "Usuario no encontrado")

            role_name = user.role
            user_email = user.email

            connection.commit()

            # Creamos la tarea para enviar el correo de bienvenida
            send_welcome_registration_email.delay(
                user_name=data.name,
                user_first_surname=data.first_surname,
                user_email=user_email
            )

            # Creamos los tokens de acceso
            access_token = create_access_token(
                {
                    "sub": str(user_id),
                    "role": role_name,
                    "parking_id": parking_id,
                    "onboarding_completed": True
                },
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)
            )

            refresh_token = create_refresh_token({
                "sub": str(user_id),
                "role": role_name,
                "parking_id": parking_id,
                "onboarding_completed": True
            })

            set_auth_cookies(response, access_token, refresh_token)

            return None, True, "Onboarding completado"

        except ServiceError as e:
            connection.rollback()
            return e.message, False, None

        except Exception as e:
            connection.rollback()
            logger.error("Error en complete_onboarding: %s", e, exc_info=True)
            return "Error al intentar completar el onboarding", False, None

        finally:
            connection.close()

    @staticmethod
    async def refresh_tokens(request: Request, response: Response):
        refresh_token = request.cookies.get("refresh_token")

        if not refresh_token:
            raise ServiceError("Refresh token no encontrado")

        try:
            payload = jwt.decode(
                refresh_token,
                settings.REFRESH_TOKEN_SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

            user_id = payload.get("sub")
            parking_id = payload.get("parking_id")

            if not user_id:
                raise ServiceError("Refresh token inválido")

            # Calculamos el tiempo que le queda para que expire
            ttl = get_token_remaining_ttl(refresh_token)

            # Agregamos el token con el tiempo que le queda de expiración a la blacklist
            added = await add_to_blacklist(refresh_token, ttl)

            if not added and ttl > 0:
                logger.warning(
                    "No se pudo blacklistear el refresh_token viejo en refresh_tokens"
                )

            new_access_token = create_access_token({
                "sub": str(user_id),
                "role": payload.get("role"),
                "parking_id": parking_id,
                "onboarding_completed": payload.get("onboarding_completed", False)
            },
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)
            )

            new_refresh_token = create_refresh_token({
                "sub": user_id,
                "role": payload.get("role"),
                "parking_id": parking_id,
                "onboarding_completed": payload.get("onboarding_completed", False)
            })

            set_auth_cookies(response, new_access_token, new_refresh_token)

            return None, True, "Tokens actualizados correctamente"

        except PyJWTError:
            raise ServiceError(
                "Refresh token expirado o inválido"
            )

        except ServiceError as e:
            return e.message, False, None

        except Exception as e:
            logger.error("Error en refresh_tokens: %s", e, exc_info=True)
            return "Error al intentar refrezcar los tokens", False, None

    @staticmethod
    async def logout(request: Request, response: Response):
        try:
            access_token = request.cookies.get("access_token")
            refresh_token = request.cookies.get("refresh_token")

            response.delete_cookie(
                key="access_token",
                path="/"
            )

            response.delete_cookie(
                key="refresh_token",
                path="/api/auth/refresh"
            )

            if access_token:
                # Calculamos el tiempo que le queda para que expire
                ttl = get_token_remaining_ttl(access_token)

                # Agregamos el token con el tiempo que le queda de expiración a la blacklist
                added = await add_to_blacklist(access_token, ttl)

                if not added and ttl > 0:
                    logger.warning(
                        "No se pudo blacklistear el access_token en logout"
                    )

            if refresh_token:
                # Calculamos el tiempo que le queda para que expire
                ttl = get_token_remaining_ttl(refresh_token)

                # Agregamos el token con el tiempo que le queda de expiración a la blacklist
                added = await add_to_blacklist(refresh_token, ttl)

                if not added and ttl > 0:
                    logger.warning(
                        "No se pudo blacklistear el refresh_token en logout"
                    )

            return None, True, "Sesión cerrada exitosamente"

        except Exception as e:
            logger.error("Error en logout: %s", e, exc_info=True)
            return "Error al intentar cerrar la sesión", False, None

    @staticmethod
    def recover_password(email: EmailStr):
        try:
            error, user = UsersService.get_user_by_email(email)

            if user:
                recovery_password_email.delay(
                    user_email=email,
                    user_name=user[2]
                )

        except Exception:
            pass

        return True, "Correo enviado correctamente"
