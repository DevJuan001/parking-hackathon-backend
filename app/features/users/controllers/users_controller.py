from fastapi import HTTPException

from app.features.users.models.users_schemas import (
    CreateUserSchema,
    UpdateCurrentUserSchema,
    UpdatePasswordSchema,
    UpdateUserSchema,
    UsersFiltersSchema,
)
from app.features.users.services.users_service import UsersService
from app.middlewares.jwt_middleware import AuthPayload


class UsersController:

    @staticmethod
    def get_all_users(filters: UsersFiltersSchema, payload: AuthPayload):
        error, users = UsersService.get_all_users(
            payload.parking_id,
            filters
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": users
        }

    @staticmethod
    def get_user_stats(payload: AuthPayload):
        error, stats = UsersService.get_user_stats(
            payload.parking_id
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": stats
        }

    @staticmethod
    def get_user_by_id(user_id: int, payload: AuthPayload):
        error, user = UsersService.get_user_by_id(
            payload.parking_id,
            user_id
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": user
        }

    @staticmethod
    def get_current_user(payload: AuthPayload):
        error, user = UsersService.get_user_by_id_global(
            payload.user_id
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": user,
            "onboarding_completed": payload.onboarding_completed
        }

    @staticmethod
    def get_user_by_email(email: str):
        error, user = UsersService.get_user_by_email(email)

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": user
        }

    @staticmethod
    def get_all_roles():
        error, data = UsersService.get_all_roles()

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": data
        }

    @staticmethod
    def get_all_surnames(payload: AuthPayload):
        error, data = UsersService.get_all_surnames(
            payload.parking_id
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": data
        }

    @staticmethod
    def get_all_cities():
        error, cities = UsersService.get_all_cities()

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": cities
        }

    @staticmethod
    async def create_user(user_data: CreateUserSchema, payload: AuthPayload):
        error, success, message = await UsersService.create_user(
            user_data,
            payload.parking_id
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "success": success,
            "message": message
        }

    @staticmethod
    def update_user(user_id: int, user_data: UpdateUserSchema, payload: AuthPayload):
        error, success, message = UsersService.update_user(
            payload.parking_id,
            user_id,
            user_data
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "success": success,
            "message": message,
        }

    @staticmethod
    def update_current_user(user_data: UpdateCurrentUserSchema, payload: AuthPayload):
        error, success, message = UsersService.update_user(
            payload.parking_id,
            payload.user_id,
            user_data
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "success": success,
            "message": message
        }

    @staticmethod
    def update_user_password(password_data: UpdatePasswordSchema, payload: AuthPayload):
        error, success, message = UsersService.update_user_password(
            payload.parking_id,
            password_data,
            payload.user_id
        )

        if error:
            if error == "Contraseña incorrecta":
                raise HTTPException(status_code=401, detail=error)
            raise HTTPException(status_code=404, detail=error)

        return {
            "success": success,
            "message": message
        }

    @staticmethod
    def disable_user(user_id: int, payload: AuthPayload):
        error, success, message = UsersService.disable_user(
            payload.parking_id,
            user_id
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "success": success,
            "message": message
        }

    @staticmethod
    def enable_user(user_id: int, payload: AuthPayload):
        error, success, message = UsersService.enable_user(
            payload.parking_id,
            user_id
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "success": success,
            "message": message
        }
