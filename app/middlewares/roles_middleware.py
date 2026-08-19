
from typing import Annotated

from fastapi import Depends, HTTPException

from app.middlewares.jwt_middleware import verify_jwt
from app.middlewares.jwt_payload import JWTPayload


def require_roles(roles: list[str]):
    """
    Función para establecer que se requiere un rol para entrar a cierta ruta que este protegida

    Args:
        roles (List[str]): 

    Returns:
        role_verifier: Otra función que dentro valida el rol desestructurando el objeto payload
    """
    def role_verifier(payload: Annotated[JWTPayload, Depends(verify_jwt)]) -> JWTPayload:
        """
        Función para verificar el rol del usuario

        Args:
            payload: Una clase que dentro almacena los datos del usuario como su rol y el id
            y la firma o llave secreta del jwt.

        Returns:
           payload:
        """

        # Validación de la existencia del rol dentro de la lista roles
        if payload.role not in roles:
            raise HTTPException(
                status_code=403,
                detail="No puedes realizar esta acción"
            )

        return payload
    return role_verifier
