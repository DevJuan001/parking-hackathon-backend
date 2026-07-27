from fastapi import HTTPException

from app.features.reservations.models.reservations_schema import FilterReservationsSchema
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
