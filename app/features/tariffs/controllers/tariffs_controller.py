from fastapi import HTTPException

from app.features.tariffs.models.tariffs_schemas import (
    CreateTariffSchema,
    UpdateTariffSchema,
)
from app.features.tariffs.services.tariffs_service import TariffsService
from app.middlewares.jwt_middleware import AuthPayload


class TariffsController:

    @staticmethod
    def get_all_tariffs(payload: AuthPayload):
        error, tariffs = TariffsService.get_all_tariffs(
            payload.parking_id
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": tariffs
        }

    @staticmethod
    def get_tariff_by_id(tariff_id: int, payload: AuthPayload):
        error, tariff = TariffsService.get_tariff_by_id(
            payload.parking_id,
            tariff_id
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": tariff
        }

    @staticmethod
    def get_available_vehicle_types(payload: AuthPayload):
        error, vehicle_types = TariffsService.get_available_vehicle_types(
            payload.parking_id
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": vehicle_types
        }

    @staticmethod
    async def create_tariff(tariff_data: CreateTariffSchema, payload: AuthPayload):
        error, success, message = await TariffsService.create_tariff(
            payload.parking_id,
            tariff_data
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "success": success,
            "message": message
        }

    @staticmethod
    def update_tariff(tariff_id: int, tariff_data: UpdateTariffSchema, payload: AuthPayload):
        error, success, message = TariffsService.update_tariff(
            payload.parking_id,
            tariff_id,
            tariff_data
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "success": success,
            "message": message
        }

    @staticmethod
    def delete_tariff(tariff_id: int, payload: AuthPayload):
        error, success, message = TariffsService.delete_tariff(
            payload.parking_id,
            tariff_id
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "success": success,
            "message": message
        }
