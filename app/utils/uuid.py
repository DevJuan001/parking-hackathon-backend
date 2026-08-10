import uuid


def generate_uuid() -> str:
    """UUID v4 random como string RFC 4122 con guiones.
    Formato: 'f47ac10b-58cc-4372-a567-0e02b2c3d479'.
    Default para columnas CHAR(36) y para uso en JWT/QR.
    """
    return str(uuid.uuid4())
