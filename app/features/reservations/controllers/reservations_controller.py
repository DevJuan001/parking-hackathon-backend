from fastapi import HTTPException

from app.features.reservations.models.reservations_schemas import (
    CreateReservationSchema,
    CreateSelfReservationSchema,
    FilterReservationsSchema,
    UpdateReservationSchema,
)
from app.features.reservations.services.reservations_service import ReservationsService


class ReservationsController:
    @staticmethod
    def get_all_reservations(filters: FilterReservationsSchema, payload: dict):
        error, reservations = ReservationsService.get_all_reservations(
            filters, str(payload["parking_id"])
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "data": reservations
        }

    @staticmethod
    def create_reservation_for_user(data: CreateReservationSchema, payload: dict):
        error, success, message = ReservationsService.create_reservation(
            str(payload["parking_id"]),
            data.name,
            data.plate,
            data.email,
            data.level,
            data.start_date,
            data.start_time,
            data.end_date,
            data.end_time,
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "success": success,
            "message": message
        }

    @staticmethod
    def create_reservation_for_self(data: CreateSelfReservationSchema):
        error, success, message = ReservationsService.create_reservation(
            data.parking_id,
            data.name,
            data.plate,
            data.email,
            data.level,
            data.start_date,
            data.start_time,
            data.end_date,
            data.end_time,
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "success": success,
            "message": message
        }

    @staticmethod
    def update_reservation(reservation_id: int, data: UpdateReservationSchema, payload: dict):
        error, success, message = ReservationsService.update_reservation(
            reservation_id, data, str(payload["parking_id"])
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "success": success,
            "message": message
        }

    @staticmethod
    def delete_reservation(reservation_id: int, payload: dict):
        error, success, message = ReservationsService.delete_reservation(
            reservation_id, str(payload["parking_id"])
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "success": success,
            "message": message
        }
