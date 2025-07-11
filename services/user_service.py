from database import Database
from bson import ObjectId

# Endpoints permitidos por rol si el usuario no tiene lista propia
ROLE_PERMISSIONS = {
    'super_admin': [
        '/api/users',
        '/api/empresas',
        '/api/admin',
        '/empresas'
    ],
    'admin': [
        '/api/admin/activity',
        '/api/admin/distribution',
        '/api/empresas/<empresa_id>/activity'
    ],
    'empresa': [
        '/api/empresas',
        '/empresas'
    ],
}

class UserService:
    def __init__(self):
        self.db = Database().get_database()
    
    def get_user_by_id(self, user_id: str):
        """
        Obtiene datos del usuario por ID de forma segura.
        Solo retorna información necesaria para autenticación.
        """
        try:
            # Buscar en administradores
            user = self.db.administradores.find_one({'_id': ObjectId(user_id)})
            collection = 'administradores'
            
            if not user:
                # Buscar en empresas
                user = self.db.empresas.find_one({'_id': ObjectId(user_id)})
                collection = 'empresas'
            
            if not user:
                return None
            
            # Verificar si está activo
            is_active = user.get('activo') if collection == 'administradores' else user.get('activa', True)
            if is_active is None:
                is_active = user.get('is_active', True)
            
            if not is_active:
                return None
            
            # Obtener rol
            role = user.get('role') or user.get('rol')
            if not role and collection == 'empresas':
                role = 'empresa'
            
            # Obtener permisos
            user_perms = user.get('permisos') or ROLE_PERMISSIONS.get(role, [])
            
            # Retornar solo información necesaria
            return {
                'id': str(user['_id']),
                'email': user.get('email'),
                'username': user.get('username') or user.get('usuario'),
                'role': role,
                'permisos': user_perms,
                'is_super_admin': role == 'super_admin'
            }
            
        except Exception as e:
            print(f"Error obteniendo usuario: {str(e)}")
            return None
