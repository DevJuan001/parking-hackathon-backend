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
    spot_id: int,
    floor_id: int | None = None,
    spot_number: str | None = None,
    vehicle_type_id: int | None = None,
) -> dict:
    error, success, message = SpotsService.update_spot(
        parking_id, spot_id, floor_id, spot_number, None, vehicle_type_id
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


def tool_delete_spot(parking_id: int, spot_id: int) -> dict:
    error, success, message = SpotsService.delete_spot(parking_id, spot_id)

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
