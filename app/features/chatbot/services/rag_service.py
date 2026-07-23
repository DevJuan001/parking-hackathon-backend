import asyncio
import json
import openai
from openai import AsyncOpenAI

from app.core.config import settings
from app.utils.logger import get_logger
from app.features.chatbot.services.context_builder import ContextBuilder
from app.features.chatbot.repositories.vector_repository import VectorRepository
from app.features.chatbot.services.conversation_service import ConversationService
from app.features.chatbot.services.intent_classifier import IntentClassifier, Intent
from app.features.chatbot.services.tool_registry import get_tool_definitions, execute_tool

logger = get_logger("chatbot.rag_service")

SYSTEM_PROMPT_PATH = "app/features/chatbot/prompts/system.txt"

# Cliente async singleton: reutiliza conexiones HTTP entre requests
# y no bloquea el event loop mientras espera la respuesta del modelo
openai_client: AsyncOpenAI | None = None


def get_openai_client() -> AsyncOpenAI:
    global openai_client

    if openai_client is None:
        openai_client = AsyncOpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_BASE_URL,
        )

    return openai_client


class RAGService:

    @staticmethod
    def load_system_prompt(snapshot: str, rag_chunks: list[dict]) -> str:
        # Abrimos el system prompt file en "utf-8"
        with open(SYSTEM_PROMPT_PATH, encoding="utf-8") as file:
            base = file.read()

        # Si hay información guardada en la base de datos vectorial la guardamos en context_text
        if rag_chunks:
            context_text = "\n\n".join(
                f"[{chunk['source']} - {chunk.get('category', 'general')}]\n{chunk['text']}"
                for chunk in rag_chunks
            )
        else:
            context_text = "No hay información adicional disponible."

        # Devolvemos el system prompt para indicarle al modelo las reglas a seguir, junto a la captura de los datos actuales del parking
        # Junto al contexto almacenado en la base de datos vectorial
        return f"{base}\n\n## ESTADO ACTUAL DEL PARKING:\n{snapshot}\n\n## INFORMACIÓN DE REFERENCIA:\n{context_text}"

    @staticmethod
    async def ask(message: str, user_payload: dict) -> dict:
        # Clasificamos la intención del mensaje
        intent = IntentClassifier.classify(message)

        if intent == Intent.INJECTION_ATTEMPT:
            return {
                "response": "No puedo procesar esa solicitud. Por favor haz una pregunta sobre la gestión del estacionamiento.",
                "actions": [],
                "sources": [],
            }

        parking_id = user_payload.get("parking_id")
        user_id = user_payload.get("user_id")
        role = user_payload.get("role", "Cliente")

        # Obtenemos una captura (snapshot) del estado actual del parking:
        # pisos, plazas, ocupación y recaudación del día (esta última solo para Admin).
        # Va a un thread porque mysql-connector es síncrono
        snapshot = await asyncio.to_thread(
            ContextBuilder.build_snapshot, parking_id, role
        )

        # Buscamos la información almacenada en la base de datos vectorial
        # (también a un thread: qdrant-client y el encode de embeddings son síncronos)
        error, rag_chunks = await asyncio.to_thread(
            VectorRepository.search_chunks,
            parking_id, message, limit=5
        )

        if error:
            rag_chunks = []

        # Buscamos si ya existe una conversación con el usuario
        try:
            history = await ConversationService.get_history(parking_id, user_id, limit=10)

        except Exception as e:
            logger.warning(
                "No se pudo cargar el historial de conversación: %s", e
            )
            history = []

        # Buscamos el system prompt que contiene las reglas que debe seguir el modelo
        system_prompt = RAGService.load_system_prompt(snapshot, rag_chunks)

        # Creamos un array de mensajes con el rol del modelo y el system prompt
        messages: list[dict] = [{
            "role": "system",
            "content": system_prompt
        }]

        # Agregamos la conversación anterior si existe
        messages.extend(history)

        # Añadimos el nuevo mensaje del usuario al array de mensajes
        messages.append({
            "role": "user",
            "content": message
        })

        # Guardamos el índice para saber qué mensajes son nuevos en esta request
        # y poder guardarlos al historial con tool_calls incluidos
        save_start = len(messages)

        # Verificamos que exista el AI_API_KEY en las variables de entorno
        if not settings.AI_API_KEY:
            return {
                "response": "El asistente no está configurado. Contactá al administrador del sistema.",
                "actions": [],
                "sources": [],
            }

        # Obtenemos el cliente async de OpenAI (singleton, no bloquea el event loop)
        client = get_openai_client()

        # Obtenemos todas las herramientas o funciones que puede ejecutar el modelo
        tools = get_tool_definitions()

        all_actions = []

        all_sources = set()

        # Guardamos los nombres de las fuentes usadas, para poder citarlas en la respuesta
        for chunk in rag_chunks:
            all_sources.add(chunk["source"])

        # Establecemos un límite de seguridad contra bucles infinitos de tool calls:
        # el modelo podría pedir herramientas una y otra vez, y cada iteración es una llamada paga a OpenAI
        max_iterations = 5

        for iteration in range(max_iterations):
            try:
                # Esperamos la respuesta del modelo dándole todo el contexto y herramientas
                response = await client.chat.completions.create(
                    model=settings.AI_MODEL,
                    messages=messages,
                    tools=tools or None,
                    tool_choice="auto" if tools else None,
                    temperature=settings.AI_TEMPERATURE,
                    max_tokens=settings.AI_MAX_TOKENS,
                )

            except openai.BadRequestError:
                logger.warning(
                    "Tool calls no soportados por el modelo, reintentando sin tools"
                )
                tools = []

                # Reintentamos obtener la respuesta del modelo pero sin usar herramientas
                response = await client.chat.completions.create(
                    model=settings.AI_MODEL,
                    messages=messages,
                    temperature=settings.AI_TEMPERATURE,
                    max_tokens=settings.AI_MAX_TOKENS,
                )

            # Almacenamos la primera decisión que el modelo elige
            choice = response.choices[0]

            # Guardamos el mensaje dentro de la decisión tomada por el modelo
            assistant_msg = choice.message

            # El LLM decidió responder directamente, sin herramientas
            if not assistant_msg.tool_calls:
                final_content = assistant_msg.content or ""

                messages.append({
                    "role": "assistant",
                    "content": final_content
                })

                break

            # Procesamos y almacenamos las herramientas que el modelo eligió usar
            tool_messages: list[dict] = [{
                "role": "assistant",
                "content": assistant_msg.content or "",
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    }
                    for tool_call in assistant_msg.tool_calls
                ]}]

            # Recorremos cada herramienta elegida por el modelo
            for tool_call in assistant_msg.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                logger.info(
                    "Tool llamado: %s | args: %s | usuario: %s",
                    func_name, func_args, user_id
                )

                # Ejecutamos cada herramienta elegida
                result = await execute_tool(func_name, func_args, user_payload)

                # Almacenamos cada herramienta ejecutada y su respuesta
                action = {
                    "tool": func_name,
                    "params": func_args,
                    "status": "ok" if "success" in result else "error",
                    "result": result.get("data") or result.get("error"),
                }

                all_actions.append(action)

                # Devolvemos el resultado al modelo para que arme su respuesta final
                tool_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False, default=str),
                })

            # Agregamos todos los mensajes de las herramientas al array de mensajes
            messages.extend(tool_messages)

            # Si llegamos a la última iteración y el modelo SIGUE pidiendo herramientas,
            # lo forzamos a responder sin tools para no salir del loop sin respuesta
            if iteration == max_iterations - 1:
                final_response = await client.chat.completions.create(
                    model=settings.AI_MODEL,
                    messages=messages,
                    temperature=settings.AI_TEMPERATURE,
                    max_tokens=settings.AI_MAX_TOKENS,
                )

                final_content = final_response.choices[0].message.content or ""

                messages.append({
                    "role": "assistant",
                    "content": final_content
                })

        # Guardamos la conversación en el historial, incluyendo tool_calls y resultados
        # para que el modelo recuerde qué herramientas ejecutó en turnos anteriores.
        try:
            await ConversationService.add_message(
                parking_id, user_id, "user", message
            )

            for msg in messages[save_start:]:
                await ConversationService.add_message(
                    parking_id, user_id,
                    role=msg["role"],
                    content=msg.get("content", ""),
                    tool_calls=msg.get("tool_calls"),
                    tool_call_id=msg.get("tool_call_id"),
                )

        except Exception as e:
            logger.warning(
                "No se pudo guardar el historial de conversación: %s", e
            )

        return {
            "response": final_content,
            "actions": all_actions or None,
            "sources": list(all_sources) if all_sources else None,
        }
