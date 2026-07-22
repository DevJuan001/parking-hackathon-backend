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


def tool_update_floor(parking_id: int, floor_id: int, name: str) -> dict:
    error, success, message = FloorsService.update_floor(
        parking_id, floor_id, name)

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


def tool_delete_floor(parking_id: int, floor_id: int) -> dict:
    error, success, message = FloorsService.delete_floor(parking_id, floor_id)

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
