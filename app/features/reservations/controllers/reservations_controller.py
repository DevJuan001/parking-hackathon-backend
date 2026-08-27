from fastapi import HTTPException

from app.features.reservations.models.reservations_schemas import (
    CreateReservationSchema,
    CreateSelfReservationSchema,
    FilterReservationsSchema,
    UpdateReservationSchema,
)
from app.features.reservations.services.reservations_service import ReservationsService
from app.middlewares.jwt_middleware import AuthPayload


class ReservationsController:
    @staticmethod
    def get_all_reservations(filters: FilterReservationsSchema, payload: AuthPayload):
        error, reservations = ReservationsService.get_all_reservations(
            filters, payload.parking_id
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {"data": reservations}

    @staticmethod
    def create_reservation_for_user(
        data: CreateReservationSchema, payload: AuthPayload
    ):
        error, success, message = ReservationsService.create_reservation(
            payload.parking_id,
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

        return {"success": success, "message": message}

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

        return {"success": success, "message": message}

    @staticmethod
    def update_reservation(
        reservation_id: int, data: UpdateReservationSchema, payload: AuthPayload
    ):
        error, success, message = ReservationsService.update_reservation(
            reservation_id, data, payload.parking_id
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {"success": success, "message": message}

    @staticmethod
    def delete_reservation(reservation_id: int, payload: AuthPayload):
        error, success, message = ReservationsService.delete_reservation(
            reservation_id, payload.parking_id
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {"success": success, "message": message}
