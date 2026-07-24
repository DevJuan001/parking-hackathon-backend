from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter

from app.middlewares.jwt_middleware import verify_jwt
from app.middlewares.onboarding_middleware import require_onboarded
from app.features.chatbot.models.chatbot_schemas import ChatbotAskSchema
from app.features.chatbot.controllers.chatbot_controller import ChatbotController

router = APIRouter(
    prefix="/api/chatbot",
    tags=["Chatbot"],
)


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
