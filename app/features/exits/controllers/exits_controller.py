from fastapi import HTTPException

from app.features.exits.models.exits_schemas import (
    CreateExitSchema,
    ExitsFiltersSchema,
    StatsExitsFiltersSchema,
)
from app.features.exits.services.exits_service import ExitsService
from app.middlewares.jwt_middleware import AuthPayload


class ExitsController:

    @staticmethod
    def get_all_exits(filters: ExitsFiltersSchema, payload: AuthPayload):
        error, exits = ExitsService.get_all_exits(
            payload.parking_id,
            filters
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": exits
        }

    @staticmethod
    def get_exit_by_id(exit_id: int, payload: AuthPayload):
        error, exit_record = ExitsService.get_exit_by_id(
            payload.parking_id,
            exit_id
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": exit_record
        }

    @staticmethod
    def get_exits_by_plate(plate_id: int, payload: AuthPayload):
        error, exits = ExitsService.get_exits_by_plate(
            payload.parking_id,
            plate_id
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": exits
        }

    @staticmethod
    async def create_exit(exit_data: CreateExitSchema, payload: AuthPayload):
        error, success, message = await ExitsService.create_exit(
            payload.parking_id,
            exit_data
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "success": success,
            "message": message
        }

    @staticmethod
    def get_exit_stats(filters: StatsExitsFiltersSchema, payload: AuthPayload):
        error, stats = ExitsService.get_exit_stats(
            filters,
            payload.parking_id
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": stats
        }
