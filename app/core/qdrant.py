from qdrant_client import QdrantClient
from app.core.config import settings
from app.utils.logger import get_logger
from qdrant_client.http.models import VectorParams, Distance

logger = get_logger("core.qdrant")

qdrant_client: QdrantClient | None = None


def get_qdrant() -> QdrantClient:
    if qdrant_client is None:
        raise RuntimeError(
            "Qdrant no inicializado. Llamá init_qdrant() primero."
        )

    return qdrant_client


def init_qdrant() -> QdrantClient:
    global qdrant_client

    qdrant_client = QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
    )

    collections = qdrant_client.get_collections().collections

    exists = any(
        collection.name == "parking_knowledge"
        for collection in collections
    )

    if not exists:
        qdrant_client.create_collection(
            collection_name="parking_knowledge",
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE,
            ),
        )

        qdrant_client.create_payload_index(
            collection_name="parking_knowledge",
            field_name="parking_id",
            field_schema="integer",
        )

        logger.info("Colección 'parking_knowledge' creada en Qdrant")

    logger.info(
        "Qdrant conectado en %s:%s",
        settings.QDRANT_HOST,
        settings.QDRANT_PORT
    )

    return qdrant_client


def close_qdrant():
    global qdrant_client

    if qdrant_client is not None:
        qdrant_client.close()

        qdrant_client = None

        logger.info("Conexión a Qdrant cerrada")
