from fastapi import HTTPException
from app.features.parking.services.parking_service import ParkingService
from app.features.parking.models.parking_schemas import CreatePlateSchema
from app.features.spots.models.spots_schemas import SpotsFiltersSchema


class ParkingController:

    @staticmethod
    def get_all_plates(payload: dict):
        error, plates = ParkingService.get_all_plates(
            int(payload["parking_id"]))

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": plates
        }

    @staticmethod
    def get_all_vehicle_types():
        error, vehicle_types = ParkingService.get_all_vehicle_types()

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": vehicle_types
        }

    @staticmethod
    def get_all_spots(payload: dict, filters: SpotsFiltersSchema):
        error, spots = ParkingService.get_all_spots(
            int(payload["parking_id"]), filters
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": spots
        }

    @staticmethod
    def get_plate_by_name(plate: str, payload: dict):
        error, plate_response = ParkingService.get_plate_by_name(
            int(payload["parking_id"]),
            plate
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": plate_response
        }

    @staticmethod
    async def create_plate(plate_data: CreatePlateSchema, payload: dict):
        error, success, message = await ParkingService.create_plate(
            int(payload["parking_id"]),
            plate_data
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "success": success,
            "message": message
        }
