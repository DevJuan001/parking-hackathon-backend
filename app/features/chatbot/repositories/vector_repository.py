import uuid

from qdrant_client.http.models import Filter, FieldCondition, MatchValue, PointStruct

from app.core.qdrant import get_qdrant
from app.utils.logger import get_logger
from app.features.chatbot.services.embedding_service import embed_text

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

        except Exception as e:
            logger.error("Error al insertar fragmentos: %s", e, exc_info=True)
            return "Error al guardar los fragmentos de conocimiento", False

    @staticmethod
    def search_chunks(parking_id: int, query: str, limit: int = 5) -> tuple:
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

        except Exception as e:
            logger.error("Error al buscar fragmentos: %s", e, exc_info=True)
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

        except Exception as e:
            logger.error(
                "Error al eliminar fragmento %s: %s",
                chunk_id,
                e,
                exc_info=True
            )
            return "Error al eliminar el fragmento", False

    @staticmethod
    def delete_chunks_by_source(parking_id: int, source: str) -> tuple:
        qdrant = get_qdrant()

        delete_filter = Filter(
            must=[
                FieldCondition(
                    key="parking_id",
                    match=MatchValue(value=parking_id),
                ),

                FieldCondition(
                    key="source",
                    match=MatchValue(value=source),
                ),
            ]
        )

        try:
            qdrant.delete(
                collection_name=COLLECTION,
                points_selector=delete_filter,
            )

            logger.info(
                "Chunks de fuente '%s' eliminados para parking %d",
                source,
                parking_id
            )

            return None, True

        except Exception as e:
            logger.error(
                "Error al eliminar chunks por fuente: %s",
                e,
                exc_info=True
            )
            return "Error al eliminar los fragmentos por fuente", False

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

        except Exception as e:
            logger.error(
                "Error al eliminar chunks del parking %d: %s",
                parking_id,
                e,
                exc_info=True
            )
            return "Error al eliminar los fragmentos del parking", False

    @staticmethod
    def get_all_chunks(parking_id: int, limit: int = 50) -> tuple:
        qdrant = get_qdrant()

        scroll_filter = Filter(
            must=[
                FieldCondition(
                    key="parking_id",
                    match=MatchValue(value=parking_id),
                )
            ]
        )

        try:
            chunks = []
            offset = None

            while True:
                results, offset = qdrant.scroll(
                    collection_name=COLLECTION,
                    scroll_filter=scroll_filter,
                    limit=limit,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False,
                )

                for point in results:
                    chunks.append({
                        "text": point.payload.get("text", ""),
                        "source": point.payload.get("source", ""),
                        "category": point.payload.get("category", ""),
                        "score": 1.0,
                    })

                if offset is None:
                    break

            return None, chunks

        except Exception as e:
            logger.error("Error al obtener los chunks: %s", e, exc_info=True)
            return "Error al obtener los fragmentos de conocimiento", []

    @staticmethod
    def get_all_sources(parking_id: int) -> tuple:
        qdrant = get_qdrant()

        scroll_filter = Filter(
            must=[
                FieldCondition(
                    key="parking_id",
                    match=MatchValue(value=parking_id),
                )
            ]
        )

        try:
            sources = set()
            offset = None

            while True:
                results, offset = qdrant.scroll(
                    collection_name=COLLECTION,
                    scroll_filter=scroll_filter,
                    limit=100,
                    offset=offset,
                    with_payload=["source"],
                    with_vectors=False,
                )

                for point in results:
                    source = point.payload.get("source")
                    if source:
                        sources.add(source)

                if offset is None:
                    break

            return None, sorted(sources)

        except Exception as e:
            logger.error("Error al obtener las fuentes: %s", e, exc_info=True)
            return "Error al obtener las fuentes de conocimiento", []
