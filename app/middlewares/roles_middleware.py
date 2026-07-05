from fastapi import Depends, HTTPException
from typing import List
from app.middlewares.jwt_middleware import verify_jwt

def require_roles(roles: List[str]):
    """
    Función para establecer que se requiere un rol para entrar a cierta ruta que este protegida

    Args:
        roles (List[str]): 

    Returns:
        role_verifier: Otra función que dentro valida el rol desestructurando el objeto payload
    """
    def role_verifier(payload: dict = Depends(verify_jwt)):

        """
        Función para verificar el rol del usuario

        Args:
            payload (dict = Depends(verify_jwt)): Un objeto que dentro almacena los datos del usuario como su rol y el id
                y la firma o llave secreta del jwt.
        
        Returns:
           payload: 
        """

        # Obtener el rol del usuario para validarlo
        user_role = payload.get("role")

        # Validación de la existencia del rol dentro de la lista roles
        if user_role not in roles:
            raise HTTPException(
                status_code=403,
                detail="No puedes realizar esta acción"
            )
        
        return payload
    return role_verifier