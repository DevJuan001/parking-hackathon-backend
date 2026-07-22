from datetime import datetime

from app.utils.logger import get_logger
from app.features.payments.services.payments_service import PaymentsService
from app.features.payments.models.payments_schemas import (
    CreatePaymentSchema,
    PaymentsFiltersSchema,
)

logger = get_logger("chatbot.tools.payments")


def tool_list_payments(parking_id: int) -> dict:
    filters = PaymentsFiltersSchema()

    error, data = PaymentsService.get_all_payments(parking_id, filters)

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
        "data": [payment.model_dump() for payment in data]
    }


def tool_calculate_payment(parking_id: int, plate: str) -> dict:
    error, data = PaymentsService.calculate_payment(parking_id, plate)

    if error:
        return {
            "error": error
        }

    return {
        "success": True,
        "data": data.model_dump()
    }


async def tool_create_payment(
    parking_id: int, plate: str, exit_time: datetime, payment_method: int
) -> dict:
    payment_data = CreatePaymentSchema(
        plate=plate, exit_time=exit_time, payment_method=payment_method
    )

    error, success, message = await PaymentsService.create_payment(parking_id, payment_data)

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
