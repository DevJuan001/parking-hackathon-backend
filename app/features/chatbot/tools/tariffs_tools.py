from app.utils.logger import get_logger
from app.features.tariffs.services.tariffs_service import TariffsService
from app.features.tariffs.models.tariffs_schemas import CreateTariffSchema, UpdateTariffSchema

logger = get_logger("chatbot.tools.tariffs")


def tool_list_tariffs(parking_id: int) -> dict:
    error, data = TariffsService.get_all_tariffs(parking_id)

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
        "data": [t.model_dump() for t in data]
    }


async def tool_create_tariff(parking_id: int, vehicle_type_id: int, rate_per_hour: float) -> dict:
    tariff_data = CreateTariffSchema(
        vehicle_type=vehicle_type_id, value=rate_per_hour)

    error, success, message = await TariffsService.create_tariff(parking_id, tariff_data)

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


def tool_update_tariff(parking_id: int, tariff_id: int, rate_per_hour: float) -> dict:
    tariff_data = UpdateTariffSchema(value=rate_per_hour)

    error, success, message = TariffsService.update_tariff(
        parking_id, tariff_id, tariff_data
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


def tool_delete_tariff(parking_id: int, tariff_id: int) -> dict:
    error, success, message = TariffsService.delete_tariff(
        parking_id, tariff_id
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
