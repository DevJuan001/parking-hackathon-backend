from app.utils.logger import get_logger
from app.features.entries.services.entries_service import EntriesService
from app.features.entries.models.entries_schemas import CreateEntrySchema, EntriesFiltersSchema

logger = get_logger("chatbot.tools.entries")


def tool_list_entries(parking_id: int) -> dict:
    filters = EntriesFiltersSchema()

    error, data = EntriesService.get_all_entries(parking_id, filters)

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
        "data": [entry.model_dump() for entry in data]
    }


async def tool_register_entry(parking_id: int, plate: str, spot_id: int | None = None, vehicle_type_id: int | None = None) -> dict:
    entry_data = CreateEntrySchema(plate=plate)

    error, success, message = await EntriesService.create_entry(parking_id, entry_data)

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
