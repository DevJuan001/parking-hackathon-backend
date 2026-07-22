from app.core.celery_app import celery
from app.features.chatbot.services.knowledge_generator import KnowledgeGenerator


@celery.task(bind=True, max_retries=2)
def rebuild_parking_knowledge(self, parking_id: int):
    error, success = KnowledgeGenerator.generate_all(parking_id)

    if error:
        raise self.retry(exc=Exception(error), countdown=30)

    return f"Knowledge rebuilt for parking {parking_id}"
