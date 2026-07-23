from app.utils.logger import get_logger
from app.features.floors.services.floors_service import FloorsService

logger = get_logger("chatbot.tools.floors")


def tool_list_floors(parking_id: int) -> dict:
    error, data = FloorsService.get_all_floors(parking_id)
    if error:
        return {
            "error": error
        }

    if not data:
        return {
            "success": True,
            "data": []
        }

    return {
        "success": True,
        "data": [floor.model_dump() for floor in data]
    }


def tool_create_floor(parking_id: int, name: str) -> dict:
    error, success, message = FloorsService.create_floor(parking_id, name)

    if error:
        return {
            "error": error
        }

    return {
        "success": True,
        "data": {
            "message": message
        }
    }


def _resolve_floor_id(
    parking_id: int, floor_id: int | None, floor_name: str | None
) -> tuple[str | None, int | None]:
    if floor_id is not None:
        return None, floor_id

    if floor_name is None:
        return "Debes proporcionar floor_id o floor_name", None

    return FloorsService.find_floor_id_by_name(parking_id, floor_name)


def tool_update_floor(parking_id: int, floor_id: int | None = None, floor_name: str | None = None, name: str = "", confirm: bool = False) -> dict:
    if not confirm:
        return {
            "error": "Debés confirmar esta acción. Responde 'sí', 'confirmo' o 'dale' para modificar el piso."
        }

    error, resolved_id = _resolve_floor_id(parking_id, floor_id, floor_name)

    if error or resolved_id is None:
        return {"error": error or "Piso no encontrado"}

    error, success, message = FloorsService.update_floor(
        parking_id, resolved_id, name)

    if error:
        return {
            "error": error
        }

    updated = tool_list_floors(parking_id)

    return {
        "success": True,
        "data": {
            "message": message,
            "updated_list": updated.get("data") if updated.get("success") else None,
        }
    }


def tool_delete_floor(parking_id: int, floor_id: int | None = None, floor_name: str | None = None, confirm: bool = False) -> dict:
    if not confirm:
        return {"error": "Debés confirmar esta acción. Responde 'sí', 'confirmo' o 'dale' para eliminar el piso."}

    error, resolved_id = _resolve_floor_id(parking_id, floor_id, floor_name)

    if error or resolved_id is None:
        return {
            "error": error or "Piso no encontrado"
        }

    error, success, message = FloorsService.delete_floor(
        parking_id, resolved_id)

    if error:
        return {
            "error": error
        }

    updated = tool_list_floors(parking_id)

    return {
        "success": True,
        "data": {
            "message": message,
            "updated_list": updated.get("data") if updated.get("success") else None,
        }
    }
