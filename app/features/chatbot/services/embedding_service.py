from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger("chatbot.embedding")

model = None


def get_model():
    global model
    if model is None:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(settings.EMBEDDING_MODEL)

        logger.info(
            "Modelo de embeddings '%s' cargado",
            settings.EMBEDDING_MODEL
        )

    return model


def embed_text(text: str) -> list[float]:
    model = get_model()

    return model.encode(text).tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_model()

    return model.encode(texts).tolist()
