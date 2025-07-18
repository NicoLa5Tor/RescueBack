from repositories.usuario_repository import UsuarioRepository
from repositories.empresa_repository import EmpresaRepository
from typing import Dict, Any, Optional


class PhoneLookupService:
    """
    Servicio para buscar información de una persona por su número de teléfono.
    No requiere autenticación.
    """
    
    def __init__(self):
        self.usuario_repository = UsuarioRepository()
        self.empresa_repository = EmpresaRepository()
    
    def lookup_by_phone(self, telefono: str) -> Dict[str, Any]:
        """
        Busca información de una persona por su número de teléfono.
        
        Args:
            telefono: Número de teléfono a buscar
            
        Returns:
            Dict con la información encontrada o error si no se encuentra
        """
        try:
            # Validar que el teléfono no esté vacío
            if not telefono or not telefono.strip():
                return {
                    'success': False,
                    'error': 'Teléfono requerido',
                    'message': 'El número de teléfono es obligatorio'
                }
            
            # Normalizar el teléfono
            telefono_normalizado = telefono.strip()
            
            # Buscar usuario por teléfono
            usuario = self.usuario_repository.find_by_telefono_global(telefono_normalizado)
            
            if not usuario:
                return {
                    'success': False,
                    'error': 'Usuario no encontrado',
                    'message': f'No se encontró ningún usuario con el teléfono {telefono_normalizado}'
                }
            
            # Obtener información de la empresa
            empresa = self.empresa_repository.find_by_id(usuario.empresa_id)
            
            if not empresa:
                return {
                    'success': False,
                    'error': 'Empresa no encontrada',
                    'message': 'La empresa asociada al usuario no fue encontrada'
                }
            
            # Construir respuesta con la información solicitada
            return {
                'success': True,
                'data': {
                    'id': str(usuario._id),
                    'nombre': usuario.nombre,
                    'empresa': empresa.nombre,
                    'sede': usuario.sede,
                    'telefono': usuario.telefono,
                    'cedula': usuario.cedula,
                    'rol': usuario.rol,
                    'email': usuario.email
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'Error interno',
                'message': f'Error al buscar información: {str(e)}'
            }
