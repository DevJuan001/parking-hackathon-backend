---
name: tool-registry
description: LLM tool registration contract for the chatbot (app/features/chatbot/services/tool_registry.py). Load when adding a new tool, modifying tool access by role, or changing the tool dispatch flow.
---

# Tool registry

## Where it lives

`app/features/chatbot/services/tool_registry.py`. It is a module-level `TOOLS: dict[str, dict]` that the `RAGService` queries at request time to get the OpenAI tool definitions and to dispatch tool calls.

The chatbot is **Admin-only**, and the registry is the gate that decides which `Admin` can call which tool. See the `chatbot` skill for the surrounding architecture (intent classifier, RAG, history, LLM loop).

## Pattern

`register_tool(name, description, parameters, required_roles, func)`. Each entry in `TOOLS` is a dict with five keys:

```python
TOOLS[name] = {
    "name": str,            # used in the LLM's tool_call.function.name
    "description": str,     # used in the OpenAI tool definition
    "parameters": dict,     # JSON Schema for the arguments
    "required_roles": list[str],
    "func": callable,       # the Python function that does the work
}
```

The `func` signature **must** accept `parking_id` as the first positional argument and the JSON Schema properties as keyword arguments:

```python
def tool_list_floors(parking_id: int) -> dict: ...
def tool_update_floor(
    parking_id: int,
    floor_id: int | None = None,
    floor_name: str | None = None,
    name: str = "",
    confirm: bool = False,
) -> dict: ...
```

The runtime injects `parking_id` from `user_payload["parking_id"]`. All other arguments come from the JSON Schema. `**params` is unpacked by `execute_tool` — keep your signature aligned with the schema, otherwise the LLM will hallucinate args you don't accept.

## How to add a new tool

1. **Create the tool module** at `app/features/chatbot/tools/<domain>_tools.py`. One file per domain (`floors_tools.py`, `tariffs_tools.py`, ...). Reuse the existing service-layer call.

   ```python
   # app/features/chatbot/tools/floors_tools.py
   from app.utils.logger import get_logger
   from app.features.floors.services.floors_service import FloorsService

   logger = get_logger("chatbot.tools.floors")


   def tool_list_floors(parking_id: int) -> dict:
       error, data = FloorsService.get_all_floors(parking_id)
       if error:
           return {"error": error}
       if not data:
           return {"success": True, "data": []}
       return {
           "success": True,
           "data": [floor.model_dump() for floor in data]
       }
   ```

2. **Import and register** the function in `tool_registry.py`. The import goes at the top with the rest, and the `register_tool(...)` call goes in the corresponding section (each domain has a comment block separator: `# ── PISOS ──`, `# ── TARIFAS ──`, etc.).

   ```python
   from app.features.chatbot.tools.floors_tools import tool_list_floors

   register_tool(
       name="list_floors",
       description="Lista todos los pisos registrados en el parking",
       parameters={
           "type": "object",
           "properties": {},
           "required": [],
       },
       required_roles=["Admin"],
       func=tool_list_floors,
   )
   ```

3. **Update the system prompt** if the new tool is a destructive op (CREATE / UPDATE / DELETE). The prompt's rules 4 and 5 govern confirmation gates — make sure the tool's `confirm` parameter is described in `parameters` (see `tool_update_floor` for the pattern).

4. **If the change affects the parking or tariff corpus**, enqueue a knowledge rebuild (see `app/tasks/knowledge_tasks.py` and the `chatbot` skill's `Knowledge Generator` section). The `tool_update_parking` and `tariffs` tools already do this.

5. **Test in the running app** with `curl` or a real LLM call. The tool definitions are loaded at import time, so a `uvicorn` restart is required.

## Tool execution flow

`execute_tool(name, params, user_payload)` is the single entry point used by the `RAGService`:

1. **Unknown tool** → `{"error": f"La herramienta '{name}' no existe"}`.
2. **Role check** → if `user_payload["role"]` is not in `tool["required_roles"]`, returns `{"error": "No tenés permisos para realizar esta acción"}`. This is **defense in depth**: the route is already restricted to `Admin` (see `chatbot` skill), but the registry re-checks at dispatch.
3. **Tenancy check** → requires `user_payload["parking_id"]`. Returns an error dict if missing.
4. **Dispatch**:
   - If `func` is async (`inspect.iscoroutinefunction(func)` is True): `await func(parking_id=parking_id, **params)`.
   - Otherwise: `await asyncio.to_thread(func, parking_id=parking_id, **params)`. The `to_thread` keeps the MySQL driver (sync) from blocking the event loop.
5. **Exception handling** → on any exception, returns `{"error": "Ocurrió un error inesperado al ejecutar la acción"}` and logs `Error ejecutando tool 'X': %s` with `exc_info=True`.

The function must return a `dict` with one of:

- `{"success": True, "data": <serializable>}` — successful result.
- `{"error": "<message>"}` — business error, surfaced to the LLM as a tool message.

Strings, numbers, dicts, and lists of those are serializable. Pydantic models are not — call `.model_dump()` before returning.

## Role check (defense in depth)

The role check is enforced in **two** places:

- **At registration time** (the `required_roles` list is part of the public contract — the OpenAI tool definition does not expose it, but every caller goes through `execute_tool` which checks it).
- **At execution time** (the `if user_role not in tool["required_roles"]` line in `execute_tool`).

The route also restricts to `Admin` (`require_roles(["Admin"])` in `chatbot_routes.py`). All three layers must stay. If you remove the route check, the registry still protects — but if you remove the registry check, an LLM could in principle call any tool that was registered for a different role.

Currently every registered tool has `required_roles=["Admin"]`. The `Cliente` and `Maquina` roles have no tools.

## Sync execution

Tool functions are expected to be **synchronous** because they call the sync MySQL driver (`mysql-connector-python`). The runtime wraps them in `asyncio.to_thread`. If you write an async tool (e.g. it makes an HTTP call), you can mark it `async def` and the registry will `await` it directly — but in this codebase, every tool is sync because the work is local DB I/O.

Don't use `await` inside a sync tool. Don't open a new event loop. The `to_thread` wrapper handles the off-loop dispatch.

## Example — full lifecycle for a new tool

Adding `tool_get_vehicle_type_stats(parking_id)` (hypothetical):

```python
# app/features/chatbot/tools/queries_tools.py
def tool_get_vehicle_type_stats(parking_id: int) -> dict:
    error, data = ChatbotService.get_vehicle_type_stats(parking_id)
    if error:
        return {"error": error}
    return {"success": True, "data": data}
```

```python
# app/features/chatbot/services/tool_registry.py
from app.features.chatbot.tools.queries_tools import (
    tool_get_occupancy_stats,
    tool_get_daily_summary,
    tool_get_vehicle_type_stats,   # new
)

register_tool(
    name="get_vehicle_type_stats",
    description="Obtiene la cantidad de ingresos por tipo de vehículo (auto, moto) en el parking",
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    },
    required_roles=["Admin"],
    func=tool_get_vehicle_type_stats,
)
```

After this:

- The system prompt's RAG context is unchanged (no corpus change).
- The `rebuild_parking_knowledge` task is **not** required.
- A uvicorn restart picks up the new tool.
- A user message like "¿cuántos autos entraron hoy?" will trigger the LLM to call `get_vehicle_type_stats`.

## Anti-patterns

- **Calling the repository directly from a tool.** Always go through the service layer — the service is where the transaction, the role check, and the user-facing error message live. The tool just adapts the I/O.
- **Tools that bypass the role check.** Every tool must declare `required_roles`. Tools that mutate the DB also need a `confirm` parameter in their JSON Schema if they are destructive.
- **Tools that include PII in the response.** Return aggregate stats, IDs, and labels. Don't return emails, full names, or payment values that the chatbot would then echo back.
- **Tools that call external services without a timeout.** A hanging HTTP call blocks the event loop until `asyncio.to_thread` gives up. Set a timeout explicitly.
- **Tools that write to the DB without `confirm`.** A destructive tool must require `confirm: bool` in the JSON Schema and check it before mutating. The system prompt also gates on this for CREATE / UPDATE / DELETE.
- **Long-running tools in the chat loop.** The 5-iteration cap in `RAGService` will starve other turns if a tool blocks. If the work is heavy, return a quick ack and process in the background (Celery).
- **Registering the same tool name twice.** The second `register_tool` call silently overwrites the first. Don't.
- **Returning a pydantic model directly from a tool.** The registry serializes via `json.dumps(..., default=str)` in the `RAGService`, which is fragile. Call `.model_dump()` first.

## Common errors

- `KeyError: 'parking_id'` → `user_payload` doesn't have `parking_id`. The route was probably called without `verify_jwt` or with a malformed token. Re-check the route's `Depends`.
- `Tool no existe` returned to the LLM → you renamed the tool but forgot to restart uvicorn. Restart.
- The LLM calls the tool with a string but the function expects `int` → the JSON Schema does not declare `"type": "integer"`. Fix the schema or coerce inside the tool.
- The LLM invents an extra arg → the function accepts `**kwargs` or the schema is too permissive. Tighten `properties` and `required`.
- Tool result never reaches the user → `messages.extend(tool_messages)` was skipped in the RAG iteration. Read the tool execution loop in `RAGService.ask`.

## Required environment variables

None — the tool registry is in-process Python. The surrounding chatbot does need `AI_API_KEY`, `AI_BASE_URL`, `AI_MODEL`, `QDRANT_HOST`, `QDRANT_PORT`, `EMBEDDING_MODEL` (see `config-and-settings` and the `chatbot` skill).
