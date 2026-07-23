from pydantic_settings import BaseSettings
from pydantic import EmailStr


class Settings(BaseSettings):
    """
    Esta clase carga y valida las variables de entorno definidas en el archivo ".env"
    Simplemente importa `settings` donde lo necesites y accede a sus atributos.

    Ejemplo:
        from app.core.config import settings
        print(settings.DB_HOST)

    Además si falta alguna de estas variables Pydantic mostrara un error antes de iniciar la app
    """
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    REDIS_URL: str
    ENVIRONMENT: str
    ACCESS_TOKEN_SECRET_KEY: str
    REFRESH_TOKEN_SECRET_KEY: str
    ALGORITHM: str
    REFRESH_TOKEN_EXPIRE: int
    ACCESS_TOKEN_EXPIRE: int
    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    AI_API_KEY: str
    AI_BASE_URL: str
    AI_MODEL: str
    AI_MAX_TOKENS: int = 1024
    AI_TEMPERATURE: float = 0.3
    CHATBOT_ENABLED: bool = True
    QDRANT_HOST: str
    QDRANT_PORT: int
    EMBEDDING_MODEL: str
    HF_TOKEN: str

    class Config:
        env_file = ".env"


settings = Settings()
