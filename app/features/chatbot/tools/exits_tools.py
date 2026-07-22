from app.utils.logger import get_logger
from app.features.exits.services.exits_service import ExitsService
from app.features.exits.models.exits_schemas import CreateExitSchema, ExitsFiltersSchema

logger = get_logger("chatbot.tools.exits")


def tool_list_exits(parking_id: int) -> dict:
    filters = ExitsFiltersSchema()

    error, data = ExitsService.get_all_exits(parking_id, filters)

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
        "data": [exit_record.model_dump() for exit_record in data]
    }


async def tool_register_exit(parking_id: int, plate: str, spot_id: int | None = None) -> dict:
    exit_data = CreateExitSchema(plate=plate)

    error, success, message = await ExitsService.create_exit(parking_id, exit_data)

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
