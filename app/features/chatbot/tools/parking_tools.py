from app.tasks.knowledge_tasks import rebuild_parking_knowledge
from app.utils.logger import get_logger
from app.features.parking.services.parking_service import ParkingService
from app.features.parking.models.parking_schemas import CreatePlateSchema
from app.features.chatbot.services.chatbot_service import ChatbotService

logger = get_logger("chatbot.tools.parking")


def tool_get_parking_info(parking_id: int) -> dict:
    error, data = ChatbotService.get_parking_info(parking_id)

    if error:
        return {"error": error}

    return {"success": True, "data": data}


def tool_update_parking(
    parking_id: int,
    name: str | None = None,
    address: str | None = None,
    phone: str | None = None,
) -> dict:
    error, success, message = ParkingService.update_parking(
        parking_id=parking_id,
        name=name,
        address=address,
        phone=phone,
    )

    if error:
        return {"error": error}

    if success:
        rebuild_parking_knowledge.delay(parking_id)

    return {"success": True, "data": {"message": message}}


def tool_list_plates(parking_id: int) -> dict:
    error, data = ParkingService.get_all_plates(parking_id)

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
        "data": [plate.model_dump() for plate in data]
    }


async def tool_register_plate(parking_id: int, plate: str, vehicle_type_id: int | None = None) -> dict:
    plate_data = CreatePlateSchema(plate=plate)

    error, success, message = await ParkingService.create_plate(parking_id, plate_data)

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
