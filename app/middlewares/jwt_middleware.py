import jwt
from jwt.exceptions import PyJWTError
from fastapi import Cookie, HTTPException
from app.core.config import settings
from app.core.database import get_connection


# Función para verificar el token en todas las solicitudes protegidas
async def verify_jwt(access_token: str = Cookie(None)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Token inválido o expirado",
    )

    if not access_token:
        raise credentials_exception

    try:
        payload = jwt.decode(
            access_token,
            settings.ACCESS_TOKEN_SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id = payload.get("sub")
        role = payload.get("role")

        if not user_id or not role:
            raise credentials_exception

    except PyJWTError:
        raise credentials_exception

    parking_id = _get_user_parking_id(int(user_id))
    onboarding_completed = _get_user_onboarding_status(int(user_id))

    return {
        "user_id": user_id,
        "role": role,
        "parking_id": parking_id,
        "onboarding_completed": onboarding_completed
    }


def _get_user_parking_id(user_id: int):
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT parking_id FROM USERS WHERE id = %s",
            (user_id,)
        )
        result = cursor.fetchone()
        cursor.close()

        if not result:
            return None

        return result[0]

    except Exception:
        return None

    finally:
        connection.close()


def _get_user_onboarding_status(user_id: int):
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT onboarding_completed FROM USERS WHERE id = %s",
            (user_id,)
        )
        result = cursor.fetchone()
        cursor.close()

        if not result:
            return False

        return bool(result[0])

    except Exception:
        return False

    finally:
        connection.close()
