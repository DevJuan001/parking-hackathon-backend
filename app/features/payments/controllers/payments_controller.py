from fastapi import HTTPException

from app.features.payments.models.payments_schemas import (
    CalculatePaymentSchema,
    CreatePaymentSchema,
    PaymentsFiltersSchema,
)
from app.features.payments.services.payments_service import PaymentsService
from app.middlewares.jwt_middleware import AuthPayload


class PaymentsController:
    @staticmethod
    def get_all_payments(filters: PaymentsFiltersSchema, payload: AuthPayload):
        error, payments = PaymentsService.get_all_payments(payload.parking_id, filters)

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {"data": payments}

    @staticmethod
    def get_payment_by_id(payment_id: str, payload: AuthPayload):
        error, payment = PaymentsService.get_payment_by_id(
            payload.parking_id, payment_id
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {"data": payment}

    @staticmethod
    def get_payments_growth(period: str, payload: AuthPayload):
        error, payments = PaymentsService.get_payments_growth(
            payload.parking_id,
            period,
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {"data": payments}

    @staticmethod
    def get_payments_by_plate(plate_id: int, payload: AuthPayload):
        error, payments = PaymentsService.get_payments_by_plate(
            payload.parking_id, plate_id
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {"data": payments}

    @staticmethod
    def get_all_payment_methods():
        error, methods = PaymentsService.get_all_payment_methods()

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {"data": methods}

    @staticmethod
    def calculate_payment(params: CalculatePaymentSchema, payload: AuthPayload):
        error, result = PaymentsService.calculate_payment(
            payload.parking_id, params.plate
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {"data": result}

    @staticmethod
    async def create_payment(payment_data: CreatePaymentSchema, payload: AuthPayload):
        error, success, message = await PaymentsService.create_payment(
            payload.parking_id, payment_data
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {"success": success, "message": message}
