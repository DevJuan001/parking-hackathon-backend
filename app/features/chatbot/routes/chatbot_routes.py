from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter

from app.middlewares.jwt_middleware import verify_jwt
from app.middlewares.roles_middleware import require_roles
from app.middlewares.onboarding_middleware import require_onboarded
from app.features.chatbot.models.chatbot_schemas import ChatbotAskSchema
from app.features.chatbot.controllers.chatbot_controller import ChatbotController

router = APIRouter(
    prefix="/api/chatbot",
    tags=["Chatbot"],
)


# Envía un mensaje al asistente. Puede consultar, crear, editar o eliminar recursos según los permisos del usuario
@router.post(
    "/ask",
    dependencies=[
        Depends(RateLimiter(times=20, seconds=60)),
        Depends(verify_jwt),
        Depends(require_onboarded),
    ],
)
async def ask_chatbot(
    query: ChatbotAskSchema,
    payload: dict = Depends(verify_jwt),
):
    return await ChatbotController.ask(query, payload)


# Lista las fuentes de conocimiento cargadas en el sistema
@router.get(
    "/knowledge",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(verify_jwt),
        Depends(require_roles(["Admin"])),
        Depends(require_onboarded),
    ],
)
def list_knowledge_sources(payload: dict = Depends(verify_jwt)):
    return ChatbotController.get_knowledge_sources(payload)


# Elimina una fuente de conocimiento por su nombre
@router.delete(
    "/knowledge/{source}",
    dependencies=[
        Depends(RateLimiter(times=10, seconds=60)),
        Depends(verify_jwt),
        Depends(require_roles(["Admin"])),
        Depends(require_onboarded),
    ],
)
def delete_knowledge_source(
    source: str,
    payload: dict = Depends(verify_jwt),
):
    return ChatbotController.delete_knowledge_source(source, payload)


# Reindexa todo el conocimiento desde cero
@router.post(
    "/reindex",
    dependencies=[
        Depends(RateLimiter(times=5, seconds=60)),
        Depends(verify_jwt),
        Depends(require_roles(["Admin"])),
        Depends(require_onboarded),
    ],
)
def reindex_knowledge(payload: dict = Depends(verify_jwt)):
    return ChatbotController.reindex_knowledge(payload)


# Lista los chunks de conocimiento cargados en Qdrant
@router.get(
    "/knowledge/chunks",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(verify_jwt),
        Depends(require_roles(["Admin"])),
        Depends(require_onboarded),
    ],
)
def list_knowledge_chunks(payload: dict = Depends(verify_jwt)):
    return ChatbotController.get_knowledge_chunks(payload)
