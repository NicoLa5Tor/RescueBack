from typing import Optional
from flask import Request


def get_auth_header(request: Request) -> Optional[str]:
    """
    Extrae el token JWT del header Authorization.
    
    Args:
        request: Objeto Request de Flask
        
    Returns:
        Token JWT si existe, None si no existe o es inválido
    """
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return None
    
    # Verificar que tenga formato "Bearer <token>"
    if not auth_header.startswith('Bearer '):
        return None
    
    # Extraer el token
    token = auth_header[7:]  # Remover "Bearer "
    
    if not token.strip():
        return None
    
    return token.strip()


def create_bearer_token(token: str) -> str:
    """
    Crea un header Authorization con formato Bearer token.
    
    Args:
        token: Token JWT
        
    Returns:
        String con formato "Bearer <token>"
    """
    return f"Bearer {token}"


def get_auth_cookie(request: Request, cookie_name: str = 'hardware_auth_token') -> Optional[str]:
    """
    Extrae el token JWT de una cookie.
    
    Args:
        request: Objeto Request de Flask
        cookie_name: Nombre de la cookie que contiene el token
        
    Returns:
        Token JWT si existe, None si no existe o es inválido
    """
    token = request.cookies.get(cookie_name)
    
    if not token or not token.strip():
        return None
    
    return token.strip()


def validate_token_format(token: str) -> bool:
    """
    Valida que el token tenga el formato JWT básico.
    
    Args:
        token: Token JWT a validar
        
    Returns:
        True si el formato es válido, False caso contrario
    """
    if not token or not isinstance(token, str):
        return False
    
    # Un JWT debe tener exactamente 3 partes separadas por puntos
    parts = token.split('.')
    if len(parts) != 3:
        return False
    
    # Cada parte debe tener contenido
    for part in parts:
        if not part.strip():
            return False
    
    return True
