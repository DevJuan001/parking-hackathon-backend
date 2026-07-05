from fastapi import HTTPException
from app.features.floors.services.floors_service import FloorsService
from app.features.floors.models.floors_schemas import (
    CreateFloorSchema,
    UpdateFloorSchema
)


class FloorsController:

    @staticmethod
    def get_all_floors(payload: dict):
        error, floors = FloorsService.get_all_floors(
            int(payload["parking_id"])
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": floors
        }

    @staticmethod
    def get_floor_by_id(floor_id: int, payload: dict):
        error, floor = FloorsService.get_floor_by_id(
            int(payload["parking_id"]),
            floor_id
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": floor
        }

    @staticmethod
    def create_floor(floor_data: CreateFloorSchema, payload: dict):
        error, success, message = FloorsService.create_floor(
            int(payload["parking_id"]),
            floor_data.name
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "success": success,
            "message": message
        }

    @staticmethod
    def update_floor(floor_id: int, floor_data: UpdateFloorSchema, payload: dict):
        if floor_data.name is None:
            raise HTTPException(
                status_code=400,
                detail="Debes enviar el nombre del piso a actualizar"
            )

        error, success, message = FloorsService.update_floor(
            int(payload["parking_id"]),
            floor_id,
            floor_data.name
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "success": success,
            "message": message
        }

    @staticmethod
    def delete_floor(floor_id: int, payload: dict):
        error, success, message = FloorsService.delete_floor(
            int(payload["parking_id"]),
            floor_id
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "success": success,
            "message": message
        }
