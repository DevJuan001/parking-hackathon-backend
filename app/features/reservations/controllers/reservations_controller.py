from fastapi import HTTPException

from app.features.reservations.models.reservations_schema import (
    CreateReservationSchema,
    CreateSelfReservationSchema,
    FilterReservationsSchema,
)
from app.features.reservations.services.reservations_service import ReservationsService


class ReservationsController:
    @staticmethod
    def get_all_reservations(filters: FilterReservationsSchema, payload: dict):
        error, reservations = ReservationsService.get_all_reservations(
            filters, int(payload["parking_id"])
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "data": reservations
        }

    @staticmethod
    def create_reservation_for_user(data: CreateReservationSchema, payload: dict):
        error, success, message = ReservationsService.create_reservation(
            int(payload["parking_id"]),
            data.user_id,
            data.name,
            data.level,
            data.start_date,
            data.end_date,
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {"success": success, "message": message}

    @staticmethod
    def create_reservation_for_self(data: CreateSelfReservationSchema, payload: dict):
        error, success, message = ReservationsService.create_reservation(
            int(payload["parking_id"]),
            int(payload["user_id"]),
            data.name,
            data.level,
            data.start_date,
            data.end_date,
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {"success": success, "message": message}
