from flask_jwt_extended import create_access_token
import bcrypt
from database import Database

class AuthService:
    def __init__(self):
        self.db = Database().get_database()

    def login(self, usuario, password):
        """Valida credenciales y genera un JWT"""
        try:
            user = self.db.administradores.find_one({
                '$or': [
                    {'email': usuario},
                    {'username': usuario},
                    {'usuario': usuario}
                ]
            })
            collection = 'administradores'

            if not user:
                user = self.db.empresas.find_one({'email': usuario})
                if user:
                    collection = 'empresas'
            if not user:
                return {'success': False, 'errors': ['Credenciales inválidas']}

            is_active = user.get('activo') if collection == 'administradores' else user.get('activa', True)
            if is_active is None:
                is_active = user.get('is_active', True)
            if not is_active:
                return {'success': False, 'errors': ['Credenciales inválidas']}

            stored_hash = user.get('password_hash', '')
            if not stored_hash or not bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                return {'success': False, 'errors': ['Credenciales inválidas']}

            user_perms = user.get('permisos', [])
            role = user.get('role') or user.get('rol')
            if not role and collection == 'empresas':
                role = 'empresa'
            claims = {
                'email': user.get('email'),
                'username': user.get('username') or user.get('usuario'),
                'role': role,
                'permisos': user_perms,
            }
            token = create_access_token(identity=str(user['_id']), additional_claims=claims)
            user_data = {
                'id': str(user['_id']),
                'email': user.get('email'),
                'username': user.get('username') or user.get('usuario'),
                'role': role,
                'permisos': user_perms,
                'is_super_admin': role == 'super_admin'
            }
            return {'success': True, 'token': token, 'data': user_data}
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}
