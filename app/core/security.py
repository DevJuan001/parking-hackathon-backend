from datetime import datetime, timedelta, timezone
from typing import Union
import secrets
import string
import bcrypt
import jwt
from fastapi import HTTPException, Response
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

# Ruta en la cúal los usuarios obtienen el login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def create_refresh_token(data: dict) -> str:
    expire = datetime.now(timezone.utc) + \
        timedelta(settings.REFRESH_TOKEN_EXPIRE)

    return jwt.encode(
        {**data, "exp": expire},
        settings.REFRESH_TOKEN_SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


# Función para crear el jwt con fecha de expiración
def create_access_token(
    data: dict,
    expires_delta: Union[timedelta, None] = None
) -> str:

    # Aqui guardamos una copia de el diccionario "data" dentro de "to_encode"
    to_encode = data.copy()

    # Validación
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})

    # Convierte la llave sub en una cadena de texto
    to_encode["sub"] = str(to_encode["sub"])

    # Aqui guardamos todo dentro del string del jwt
    encoded_jwt = jwt.encode(
        to_encode,
        settings.ACCESS_TOKEN_SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    IS_PRODUCTION = settings.ENVIRONMENT == "production"

    cookie_base = {
        "httponly": True,
        "secure": IS_PRODUCTION,
        "samesite": "none" if IS_PRODUCTION else "lax",
    }

    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE * 60,
        path="/",
        **cookie_base,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE * 86400,
        path="/api/auth/refresh",
        **cookie_base,
    )


# Función para verificar la contraseña del usuario
def verify_password(user_password: str, password: str):
    password_bytes = password.encode("utf-8")
    hashed_bytes = user_password.encode("utf-8")

    if not bcrypt.checkpw(password_bytes, hashed_bytes):
        return False

    return True


# Funcion para crear un contraseña temporal
def generate_temporal_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%&*"

    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
    ]

    password += [secrets.choice(alphabet) for _ in range(length - 3)]

    # Mezcla para que no sean predecibles las primeras posiciones
    secrets.SystemRandom().shuffle(password)

    return ''.join(password)
