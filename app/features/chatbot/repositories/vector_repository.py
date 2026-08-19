import uuid

from qdrant_client.http.models import FieldCondition, Filter, MatchValue, PointStruct

from app.core.qdrant import get_qdrant
from app.features.chatbot.services.embedding_service import embed_text
from app.utils.logger import get_logger

logger = get_logger("chatbot.vector_repository")

COLLECTION = "parking_knowledge"


class VectorRepository:

    @staticmethod
    def upsert_chunks(parking_id: int, chunks: list[dict]) -> tuple:
        qdrant = get_qdrant()

        texts = [chunk["text"] for chunk in chunks]
        embeddings = embed_text(texts)

        points = []
        
        for chunk, vector in zip(chunks, embeddings):
            chunk_id = str(uuid.uuid5(uuid.NAMESPACE_URL, chunk["id"]))

            points.append(PointStruct(
                id=chunk_id,
                vector=vector,
                payload={
                    "parking_id": parking_id,
                    "text": chunk["text"],
                    "source": chunk["source"],
                    "category": chunk["category"],
                    "chunk_index": chunk["chunk_index"],
                    "id": chunk["id"],
                }
            ))

        try:
            qdrant.upsert(
                collection_name=COLLECTION,
                points=points,
            )

            logger.info(
                "%d chunks guardados para el parking %d",
                len(points),
                parking_id
            )

            return None, True

        except Exception:
            logger.exception("Error al insertar fragmentos")
            return "Error al guardar los fragmentos de conocimiento", False

    @staticmethod
    def search_chunks(parking_id: str, query: str, limit: int = 5) -> tuple:
        qdrant = get_qdrant()

        query_vector = embed_text(query)

        search_filter = Filter(
            must=[
                FieldCondition(
                    key="parking_id",
                    match=MatchValue(value=parking_id),
                )
            ]
        )

        try:
            result = qdrant.query_points(
                collection_name=COLLECTION,
                query=query_vector,
                query_filter=search_filter,
                limit=limit,
            )

            results = result.points

            chunks = [
                {
                    "text": hit.payload["text"],
                    "source": hit.payload.get("source", ""),
                    "category": hit.payload.get("category", ""),
                    "score": hit.score,
                }
                for hit in results
            ]

            return None, chunks

        except Exception:
            logger.exception("Error al buscar fragmentos")
            return "Error al buscar en la base de conocimiento", []

    @staticmethod
    def delete_chunk(chunk_id: str) -> tuple:
        qdrant = get_qdrant()

        try:
            qdrant.delete(
                collection_name=COLLECTION,
                points_selector=[chunk_id],
            )

            logger.info("Fragmento %s eliminado", chunk_id)

            return None, True

        except Exception:
            logger.exception("Error al eliminar fragmento %s", chunk_id)
            return "Error al eliminar el fragmento", False

    @staticmethod
    def delete_all_by_parking(parking_id: int) -> tuple:
        qdrant = get_qdrant()

        delete_filter = Filter(
            must=[
                FieldCondition(
                    key="parking_id",
                    match=MatchValue(value=parking_id),
                ),
            ]
        )

        try:
            qdrant.delete(
                collection_name=COLLECTION,
                points_selector=delete_filter,
            )

            logger.info(
                "Todos los chunks eliminados para parking %d",
                parking_id
            )

            return None, True

        except Exception:
            logger.exception("Error al eliminar chunks del parking %d", parking_id)
            return "Error al eliminar los fragmentos del parking", False


