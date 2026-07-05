from celery import Celery

from app.core.config import settings

celery = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.email_tasks"]
)

"""
    Esta es una instancia de Celery configurada con:
    
    - broker: URL de Redis para recibir tareas enviadas desde la API.
    - backend: URL de Redis para almacenar resultados y estado de las tareas.
    - include: lista de módulos de tareas que el worker descubre o utilizara al iniciar.
"""

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Bogota",
    enable_utc=True,
)
