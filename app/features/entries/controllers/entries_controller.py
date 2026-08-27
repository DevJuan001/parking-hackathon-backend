from fastapi import HTTPException

from app.features.entries.models.entries_schemas import (
    CreateEntrySchema,
    EntriesFiltersSchema,
)
from app.features.entries.services.entries_service import EntriesService
from app.middlewares.jwt_middleware import AuthPayload


class EntriesController:

    @staticmethod
    def get_all_entries(filters: EntriesFiltersSchema, payload: AuthPayload):
        error, entries = EntriesService.get_all_entries(
            payload.parking_id,
            filters
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": entries
        }

    @staticmethod
    def get_entry_by_id(entry_id: int, payload: AuthPayload):
        error, entry = EntriesService.get_entry_by_id(
            payload.parking_id,
            entry_id
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": entry
        }

    @staticmethod
    def get_entries_by_plate(plate_id: int, payload: AuthPayload):
        error, entries = EntriesService.get_entries_by_plate(
            payload.parking_id,
            plate_id
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": entries
        }

    @staticmethod
    def get_recent_entries(payload: AuthPayload):
        error, entries = EntriesService.get_recent_entries(
            payload.parking_id
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": entries
        }

    @staticmethod
    def get_entry_stats(payload: AuthPayload):
        error, stats = EntriesService.get_entry_stats(
            payload.parking_id
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": stats
        }

    @staticmethod
    async def create_entry(entry_data: CreateEntrySchema, payload: AuthPayload):
        error, success, message = await EntriesService.create_entry(
            payload.parking_id,
            entry_data
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "success": success,
            "message": message,
        }
