from fastapi import HTTPException
from app.features.users.services.users_service import UsersService
from app.features.users.models.users_schemas import CreateUserSchema, UpdateCurrentUserSchema, UpdatePasswordSchema, UpdateUserSchema, UsersFiltersSchema


class UsersController:

    @staticmethod
    def get_all_users(filters: UsersFiltersSchema, payload: dict):
        error, users = UsersService.get_all_users(
            int(payload["parking_id"]),
            filters
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": users
        }

    @staticmethod
    def get_user_stats(payload: dict):
        error, stats = UsersService.get_user_stats(
            int(payload["parking_id"])
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": stats
        }

    @staticmethod
    def get_user_by_id(user_id: int, payload: dict):
        error, user = UsersService.get_user_by_id(
            int(payload["parking_id"]),
            user_id
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": user
        }

    @staticmethod
    def get_current_user(payload: dict):
        error, user = UsersService.get_user_by_id_global(
            int(payload["user_id"])
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "data": user,
            "onboarding_completed": bool(payload.get("onboarding_completed"))
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
    def get_all_surnames(payload: dict):
        error, data = UsersService.get_all_surnames(
            int(payload["parking_id"])
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
    async def create_user(user_data: CreateUserSchema, payload: dict):
        error, success, message = await UsersService.create_user(
            user_data,
            int(payload["parking_id"])
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "success": success,
            "message": message
        }

    @staticmethod
    def update_user(user_id: int, user_data: UpdateUserSchema, payload: dict):
        error, success, message = UsersService.update_user(
            int(payload["parking_id"]),
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
    def update_current_user(user_data: UpdateCurrentUserSchema, payload: dict):
        error, success, message = UsersService.update_user(
            int(payload["parking_id"]),
            int(payload["user_id"]),
            user_data
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "success": success,
            "message": message
        }

    @staticmethod
    def update_user_password(password_data: UpdatePasswordSchema, payload: dict):
        error, success, message = UsersService.update_user_password(
            int(payload["parking_id"]),
            password_data,
            int(payload["user_id"])
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
    def disable_user(user_id: int, payload: dict):
        error, success, message = UsersService.disable_user(
            int(payload["parking_id"]),
            user_id
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "success": success,
            "message": message
        }

    @staticmethod
    def enable_user(user_id: int, payload: dict):
        error, success, message = UsersService.enable_user(
            int(payload["parking_id"]),
            user_id
        )

        if error:
            raise HTTPException(status_code=404, detail=error)

        return {
            "success": success,
            "message": message
        }
