from app.features.chatbot.tools.floors_tools import (
    tool_list_floors,
    tool_create_floor,
    tool_update_floor,
    tool_delete_floor,
)
from app.features.chatbot.tools.spots_tools import (
    tool_list_spots,
    tool_create_spot,
    tool_update_spot,
    tool_delete_spot,
)
from app.features.chatbot.tools.tariffs_tools import (
    tool_list_tariffs,
    tool_create_tariff,
    tool_update_tariff,
    tool_delete_tariff,
)
from app.features.chatbot.tools.entries_tools import (
    tool_list_entries,
    tool_register_entry,
)
from app.features.chatbot.tools.exits_tools import (
    tool_list_exits,
    tool_register_exit,
)
from app.features.chatbot.tools.payments_tools import (
    tool_list_payments,
    tool_calculate_payment,
    tool_create_payment,
)
from app.features.chatbot.tools.parking_tools import (
    tool_get_parking_info,
    tool_update_parking,
    tool_list_plates,
    tool_register_plate,
)
from app.features.chatbot.tools.queries_tools import (
    tool_get_occupancy_stats,
    tool_get_daily_summary,
)
import asyncio
import inspect

from app.utils.logger import get_logger

TOOLS: dict[str, dict] = {}


def register_tool(
    name: str,
    description: str,
    parameters: dict,
    required_roles: list[str],
    func: callable,
):
    TOOLS[name] = {
        "name": name,
        "description": description,
        "parameters": parameters,
        "required_roles": required_roles,
        "func": func,
    }


def get_tool_definitions() -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"],
            },
        }
        for tool in TOOLS.values()
    ]


async def execute_tool(name: str, params: dict, user_payload: dict) -> dict:
    tool = TOOLS.get(name)

    if not tool:
        return {
            "error": f"La herramienta '{name}' no existe"
        }

    user_role = user_payload.get("role")

    if user_role not in tool["required_roles"]:
        return {
            "error": "No tenés permisos para realizar esta acción"
        }

    parking_id = user_payload.get("parking_id")

    if not parking_id:
        return {
            "error": "No se encontró el parking asociado a tu cuenta"
        }

    try:
        func = tool["func"]

        # Las tools sync (MySQL) van a un thread para no bloquear el event loop
        if inspect.iscoroutinefunction(func):
            result = await func(parking_id=parking_id, **params)
        else:
            result = await asyncio.to_thread(func, parking_id=parking_id, **params)

        return result

    except Exception as e:
        logger = get_logger("chatbot.tool_registry")
        logger.error("Error ejecutando tool '%s': %s", name, e, exc_info=True)
        return {"error": "Ocurrió un error inesperado al ejecutar la acción"}


# ─────────────────────────── PISOS ───────────────────────────
register_tool(
    name="list_floors",
    description="Lista todos los pisos registrados en el parking",
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    },
    required_roles=["Admin", "Cliente"],
    func=tool_list_floors,
)

register_tool(
    name="create_floor",
    description="Crea un nuevo piso en el parking",
    parameters={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Nombre del piso (ej: '1', 'PB', 'Sótano')",
            }
        },
        "required": ["name"],
    },
    required_roles=["Admin"],
    func=tool_create_floor,
)

register_tool(
    name="update_floor",
    description="Actualiza el nombre de un piso existente",
    parameters={
        "type": "object",
        "properties": {
            "floor_id": {
                "type": "integer",
                "description": "ID del piso a actualizar",
            },
            "name": {"type": "string", "description": "Nuevo nombre del piso"},
        },
        "required": ["floor_id", "name"],
    },
    required_roles=["Admin"],
    func=tool_update_floor,
)

register_tool(
    name="delete_floor",
    description="Elimina un piso y todas sus plazas (solo si no hay plazas ocupadas)",
    parameters={
        "type": "object",
        "properties": {
            "floor_id": {
                "type": "integer",
                "description": "ID del piso a eliminar",
            }
        },
        "required": ["floor_id"],
    },
    required_roles=["Admin"],
    func=tool_delete_floor,
)

# ─────────────────────────── PLAZAS ───────────────────────────
register_tool(
    name="list_spots",
    description="Lista las plazas del parking, opcionalmente filtradas por piso",
    parameters={
        "type": "object",
        "properties": {
            "floor_id": {
                "type": "integer",
                "description": "ID del piso para filtrar (opcional)",
            }
        },
        "required": [],
    },
    required_roles=["Admin", "Cliente"],
    func=tool_list_spots,
)

register_tool(
    name="create_spot",
    description="Crea una nueva plaza de estacionamiento en un piso",
    parameters={
        "type": "object",
        "properties": {
            "floor_id": {
                "type": "integer",
                "description": "ID del piso donde se creará la plaza",
            },
            "spot_number": {
                "type": "string",
                "description": "Identificador de la plaza (ej: 'A1', 'B12')",
            },
            "vehicle_type_id": {
                "type": "integer",
                "description": "ID del tipo de vehículo (1=auto, 2=moto)",
            },
        },
        "required": ["floor_id", "spot_number", "vehicle_type_id"],
    },
    required_roles=["Admin"],
    func=tool_create_spot,
)

register_tool(
    name="update_spot",
    description="Actualiza los datos de una plaza existente (piso, número, tipo de vehículo)",
    parameters={
        "type": "object",
        "properties": {
            "spot_id": {"type": "integer", "description": "ID de la plaza a actualizar"},
            "floor_id": {
                "type": "integer",
                "description": "Nuevo ID del piso (opcional)",
            },
            "spot_number": {
                "type": "string",
                "description": "Nuevo identificador de la plaza (opcional)",
            },
            "vehicle_type_id": {
                "type": "integer",
                "description": "Nuevo ID del tipo de vehículo (opcional)",
            },
        },
        "required": ["spot_id"],
    },
    required_roles=["Admin"],
    func=tool_update_spot,
)

register_tool(
    name="delete_spot",
    description="Elimina una plaza (solo si no está ocupada)",
    parameters={
        "type": "object",
        "properties": {
            "spot_id": {"type": "integer", "description": "ID de la plaza a eliminar"}
        },
        "required": ["spot_id"],
    },
    required_roles=["Admin"],
    func=tool_delete_spot,
)

# ─────────────────────────── TARIFAS ───────────────────────────
register_tool(
    name="list_tariffs",
    description="Lista todas las tarifas configuradas en el parking",
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    },
    required_roles=["Admin", "Cliente"],
    func=tool_list_tariffs,
)

register_tool(
    name="create_tariff",
    description="Crea una nueva tarifa para un tipo de vehículo",
    parameters={
        "type": "object",
        "properties": {
            "vehicle_type_id": {
                "type": "integer",
                "description": "ID del tipo de vehículo (1=auto, 2=moto)",
            },
            "rate_per_hour": {
                "type": "number",
                "description": "Tarifa por hora en pesos",
            },
        },
        "required": ["vehicle_type_id", "rate_per_hour"],
    },
    required_roles=["Admin"],
    func=tool_create_tariff,
)

register_tool(
    name="update_tariff",
    description="Actualiza el valor de una tarifa existente",
    parameters={
        "type": "object",
        "properties": {
            "tariff_id": {
                "type": "integer",
                "description": "ID de la tarifa a actualizar",
            },
            "rate_per_hour": {
                "type": "number",
                "description": "Nuevo valor por hora en pesos",
            },
        },
        "required": ["tariff_id", "rate_per_hour"],
    },
    required_roles=["Admin"],
    func=tool_update_tariff,
)

register_tool(
    name="delete_tariff",
    description="Elimina una tarifa (solo si no hay vehículos activos de ese tipo)",
    parameters={
        "type": "object",
        "properties": {
            "tariff_id": {
                "type": "integer",
                "description": "ID de la tarifa a eliminar",
            }
        },
        "required": ["tariff_id"],
    },
    required_roles=["Admin"],
    func=tool_delete_tariff,
)

# ─────────────────────────── ENTRADAS ───────────────────────────
register_tool(
    name="list_entries",
    description="Lista todos los ingresos de vehículos registrados",
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    },
    required_roles=["Admin"],
    func=tool_list_entries,
)

register_tool(
    name="register_entry",
    description="Registra el ingreso de un vehículo al parking. Si la placa no existe se crea automáticamente",
    parameters={
        "type": "object",
        "properties": {
            "plate": {
                "type": "string",
                "description": "Patente del vehículo (ej: 'ABC123')",
            }
        },
        "required": ["plate"],
    },
    required_roles=["Admin", "Cliente"],
    func=tool_register_entry,
)

# ─────────────────────────── SALIDAS ───────────────────────────
register_tool(
    name="list_exits",
    description="Lista todas las salidas de vehículos registradas",
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    },
    required_roles=["Admin", "Cliente"],
    func=tool_list_exits,
)

register_tool(
    name="register_exit",
    description="Registra la salida de un vehículo del parking",
    parameters={
        "type": "object",
        "properties": {
            "plate": {
                "type": "string",
                "description": "Patente del vehículo (ej: 'ABC123')",
            }
        },
        "required": ["plate"],
    },
    required_roles=["Admin", "Cliente"],
    func=tool_register_exit,
)

# ─────────────────────────── PAGOS ───────────────────────────
register_tool(
    name="list_payments",
    description="Lista todos los pagos registrados en el parking",
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    },
    required_roles=["Admin"],
    func=tool_list_payments,
)

register_tool(
    name="calculate_payment",
    description="Calcula el monto a pagar para una placa basado en el tiempo estacionado y la tarifa vigente",
    parameters={
        "type": "object",
        "properties": {
            "plate": {
                "type": "string",
                "description": "Patente del vehículo (ej: 'ABC123')",
            }
        },
        "required": ["plate"],
    },
    required_roles=["Admin", "Cliente"],
    func=tool_calculate_payment,
)

register_tool(
    name="create_payment",
    description="Registra el pago y la salida de un vehículo",
    parameters={
        "type": "object",
        "properties": {
            "plate": {
                "type": "string",
                "description": "Patente del vehículo (ej: 'ABC123')",
            },
            "exit_time": {
                "type": "string",
                "description": "Fecha y hora de salida en formato ISO 8601 (ej: '2024-12-01T14:30:00')",
            },
            "payment_method": {
                "type": "integer",
                "description": "ID del método de pago",
            },
        },
        "required": ["plate", "exit_time", "payment_method"],
    },
    required_roles=["Admin", "Cliente"],
    func=tool_create_payment,
)

# ─────────────────────────── INFORMACION GENERAL ───────────────────────────
register_tool(
    name="get_parking_info",
    description="Obtiene la información general del parking (nombre, dirección, teléfono)",
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    },
    required_roles=["Admin", "Cliente"],
    func=tool_get_parking_info,
)

register_tool(
    name="update_parking",
    description="Actualiza los datos del parking (nombre, dirección, teléfono)",
    parameters={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Nuevo nombre del parking (opcional)",
            },
            "address": {
                "type": "string",
                "description": "Nueva dirección del parking (opcional)",
            },
            "phone": {
                "type": "string",
                "description": "Nuevo teléfono del parking (opcional)",
            },
        },
        "required": [],
    },
    required_roles=["Admin"],
    func=tool_update_parking,
)

register_tool(
    name="list_plates",
    description="Lista todas las placas (patentes) registradas en el parking",
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    },
    required_roles=["Admin"],
    func=tool_list_plates,
)

register_tool(
    name="register_plate",
    description="Registra una nueva placa (patente) en el parking",
    parameters={
        "type": "object",
        "properties": {
            "plate": {
                "type": "string",
                "description": "Patente del vehículo (ej: 'ABC123')",
            }
        },
        "required": ["plate"],
    },
    required_roles=["Admin"],
    func=tool_register_plate,
)

register_tool(
    name="get_occupancy_stats",
    description="Obtiene estadísticas de ocupación del parking: total de plazas, ocupadas y libres",
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    },
    required_roles=["Admin", "Cliente"],
    func=tool_get_occupancy_stats,
)

register_tool(
    name="get_daily_summary",
    description="Obtiene un resumen del día actual: ingresos, salidas y recaudación",
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    },
    required_roles=["Admin"],
    func=tool_get_daily_summary,
)
