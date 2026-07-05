import jwt
from app.core.config import settings
from jwt.exceptions import PyJWTError
from fastapi import Cookie, HTTPException


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

        role = payload.get("role")
        user_id = payload.get("sub")
        parking_id = payload.get("parking_id")
        onboarding_completed = payload.get("onboarding_completed")

        if not user_id or not role:
            raise credentials_exception

        return {
            "user_id": user_id,
            "role": role,
            "parking_id": parking_id,
            "onboarding_completed": onboarding_completed
        }

    except PyJWTError:
        raise credentials_exception

    except Exception as e:
        raise credentials_exception
