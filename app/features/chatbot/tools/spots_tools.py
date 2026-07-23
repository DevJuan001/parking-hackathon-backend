from app.utils.logger import get_logger
from app.features.spots.services.spots_service import SpotsService
from app.features.spots.models.spots_schemas import SpotsFiltersSchema

logger = get_logger("chatbot.tools.spots")


def tool_list_spots(parking_id: int, floor_id: int | None = None) -> dict:
    filters = SpotsFiltersSchema()

    if floor_id is not None:
        filters.floor_id = floor_id

    error, data = SpotsService.get_all_spots(parking_id, filters)

    if error:
        return {"error": error}

    if not data:
        return {
            "success": True,
            "data": []
        }

    return {
        "success": True,
        "data": [spot.model_dump() for spot in data]
    }


def tool_create_spot(
    parking_id: int, floor_id: int, spot_number: str, vehicle_type_id: int
) -> dict:
    error, success, message = SpotsService.create_spot(
        parking_id, floor_id, spot_number, vehicle_type_id
    )

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


def tool_update_spot(
    parking_id: int,
    spot_id: int | None = None,
    spot_label: str | None = None,
    floor_id: int | None = None,
    spot_number: str | None = None,
    vehicle_type_id: int | None = None,
    confirm: bool = False,
) -> dict:
    if not confirm:
        return {"error": "Debés confirmar esta acción. Responde 'sí', 'confirmo' o 'dale' para modificar la plaza."}

    error, resolved_id = _resolve_spot_id(parking_id, spot_id, spot_label)

    if error or resolved_id is None:
        return {
            "error": error or "Plaza no encontrada"
        }

    error, success, message = SpotsService.update_spot(
        parking_id, resolved_id, floor_id, spot_number, None, vehicle_type_id
    )

    if error:
        return {
            "error": error
        }

    updated = tool_list_spots(parking_id)

    return {
        "success": True,
        "data": {
            "message": message,
            "updated_list": updated.get("data") if updated.get("success") else None,
        }
    }


def _resolve_spot_id(parking_id: int, spot_id: int | None, spot_label: str | None) -> tuple[str | None, int | None]:
    """Si no hay spot_id pero hay spot_label, resuelve la etiqueta a ID."""
    if spot_id is not None:
        return None, spot_id

    if spot_label is None:
        return "Debes proporcionar spot_id o spot_label", None

    return SpotsService.find_spot_id_by_label(parking_id, spot_label)


def tool_delete_spot(parking_id: int, spot_id: int | None = None, spot_label: str | None = None, confirm: bool = False) -> dict:
    if not confirm:
        return {
            "error": "Debés confirmar esta acción. Responde 'sí', 'confirmo' o 'dale' para eliminar la plaza."
        }

    error, resolved_id = _resolve_spot_id(parking_id, spot_id, spot_label)

    if error or resolved_id is None:
        return {"error": error or "Plaza no encontrada"}

    error, success, message = SpotsService.delete_spot(parking_id, resolved_id)

    if error:
        return {
            "error": error
        }

    updated = tool_list_spots(parking_id)

    return {
        "success": True,
        "data": {
            "message": message,
            "updated_list": updated.get("data") if updated.get("success") else None,
        }
    }
