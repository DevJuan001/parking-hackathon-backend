from fastapi import HTTPException

from app.features.spots.models.spots_schemas import (
    CreateSpotSchema,
    SpotsFiltersSchema,
    UpdateSpotSchema,
    UpdateSpotStatusSchema,
)
from app.features.spots.services.spots_service import SpotsService
from app.middlewares.jwt_middleware import AuthPayload


class SpotsController:
    @staticmethod
    def get_all_spots(filters: SpotsFiltersSchema, payload: AuthPayload):
        error, spots = SpotsService.get_all_spots(payload.parking_id, filters)

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {"data": spots}

    @staticmethod
    def get_spot_by_id(spot_id: int, payload: AuthPayload):
        error, spot = SpotsService.get_spot_by_id(payload.parking_id, spot_id)

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {"data": spot}

    @staticmethod
    def create_spot(spot_data: CreateSpotSchema, payload: AuthPayload):
        error, success, message = SpotsService.create_spot(
            payload.parking_id,
            spot_data.floor_id,
            spot_data.spot,
            spot_data.vehicle_type_id,
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {"success": success, "message": message}

    @staticmethod
    def update_spot_status(
        spot_id: int, status_data: UpdateSpotStatusSchema, payload: AuthPayload
    ):
        error, success, message = SpotsService.update_spot_status(
            payload.parking_id, spot_id, status_data.spot_status
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {"success": success, "message": message}

    @staticmethod
    def update_spot(spot_id: int, spot_data: UpdateSpotSchema, payload: AuthPayload):
        error, success, message = SpotsService.update_spot(
            payload.parking_id,
            spot_id,
            spot_data,
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {"success": success, "message": message}

    @staticmethod
    def delete_spot(spot_id: int, payload: AuthPayload):
        error, success, message = SpotsService.delete_spot(payload.parking_id, spot_id)

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {"success": success, "message": message}
