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


def _resolve_tariff_id(
    parking_id: int, tariff_id: int | None, vehicle_type_id: int | None
) -> tuple[str | None, int | None]:
    if tariff_id is not None:
        return None, tariff_id

    if vehicle_type_id is None:
        return "Debes proporcionar tariff_id o vehicle_type_id", None

    return TariffsService.find_tariff_id_by_vehicle_type(parking_id, vehicle_type_id)


def tool_update_tariff(parking_id: int, tariff_id: int | None = None, vehicle_type_id: int | None = None, rate_per_hour: float | None = None, confirm: bool = False) -> dict:
    if not confirm:
        return {
            "error": "Debés confirmar esta acción. Responde 'sí', 'confirmo' o 'dale' para modificar la tarifa."
        }

    error, resolved_id = _resolve_tariff_id(
        parking_id, tariff_id, vehicle_type_id
    )

    if error or resolved_id is None:
        return {
            "error": error or "Tarifa no encontrada"
        }

    tariff_data = UpdateTariffSchema(value=rate_per_hour)

    error, success, message = TariffsService.update_tariff(
        parking_id, resolved_id, tariff_data
    )

    if error:
        return {
            "error": error
        }

    updated = tool_list_tariffs(parking_id)

    return {
        "success": True,
        "data": {
            "message": message,
            "updated_list": updated.get("data") if updated.get("success") else None,
        }
    }


def tool_delete_tariff(parking_id: int, tariff_id: int | None = None, vehicle_type_id: int | None = None, confirm: bool = False) -> dict:
    if not confirm:
        return {
            "error": "Debés confirmar esta acción. Responde 'sí', 'confirmo' o 'dale' para eliminar la tarifa."
        }

    error, resolved_id = _resolve_tariff_id(
        parking_id, tariff_id, vehicle_type_id
    )

    if error or resolved_id is None:
        return {
            "error": error or "Tarifa no encontrada"
        }

    error, success, message = TariffsService.delete_tariff(
        parking_id, resolved_id
    )

    if error:
        return {
            "error": error
        }

    updated = tool_list_tariffs(parking_id)

    return {
        "success": True,
        "data": {
            "message": message,
            "updated_list": updated.get("data") if updated.get("success") else None,
        }
    }
