from fastapi import HTTPException
from app.features.spots.services.spots_service import SpotsService
from app.features.spots.models.spots_schemas import (
    SpotsFiltersSchema,
    CreateSpotSchema,
    UpdateSpotStatusSchema,
    UpdateSpotSchema,
)


class SpotsController:

    @staticmethod
    def get_all_spots(filters: SpotsFiltersSchema, payload: dict):
        error, spots = SpotsService.get_all_spots(
            int(payload["parking_id"]),
            filters
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": spots
        }

    @staticmethod
    def get_spot_by_id(spot_id: int, payload: dict):
        error, spot = SpotsService.get_spot_by_id(
            int(payload["parking_id"]),
            spot_id
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": spot
        }

    @staticmethod
    def create_spot(spot_data: CreateSpotSchema, payload: dict):
        error, success, message = SpotsService.create_spot(
            int(payload["parking_id"]),
            spot_data.floor_id,
            spot_data.spot,
            spot_data.vehicle_type_id,
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "success": success,
            "message": message
        }

    @staticmethod
    def update_spot_status(spot_id: int, status_data: UpdateSpotStatusSchema, payload: dict):
        error, success, message = SpotsService.update_spot_status(
            int(payload["parking_id"]),
            spot_id,
            status_data.spot_status
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "success": success,
            "message": message
        }

    @staticmethod
    def update_spot(spot_id: int, spot_data: UpdateSpotSchema, payload: dict):
        error, success, message = SpotsService.update_spot(
            int(payload["parking_id"]),
            spot_id,
            spot_data.floor_id,
            spot_data.spot,
            spot_data.spot_status,
            spot_data.vehicle_type_id,
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "success": success,
            "message": message
        }

    @staticmethod
    def delete_spot(spot_id: int, payload: dict):
        error, success, message = SpotsService.delete_spot(
            int(payload["parking_id"]),
            spot_id
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "success": success,
            "message": message
        }
