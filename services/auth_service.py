from flask_jwt_extended import create_access_token, create_refresh_token, decode_token, get_jwt_identity, verify_jwt_in_request
import bcrypt
from datetime import datetime
from bson import ObjectId
from core.database import Database
from services.session_service import SessionService

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

class AuthService:
    def __init__(self):
        self.db = Database().get_database()
        self.session_service = SessionService()

    def login(self, usuario, password, request_data=None):
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
                user = self.db.empresas.find_one({
                    '$or': [
                        {'email': usuario},
                        {'username': usuario}
                    ]
                })
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

            role = user.get('role') or user.get('rol')
            if not role and collection == 'empresas':
                role = 'empresa'
            user_perms = user.get('permisos') or ROLE_PERMISSIONS.get(role, [])
            # JWT con información mínima por seguridad
            claims = {
                'role': role,  # Solo el rol, nada más
            }
            access_token = create_access_token(identity=str(user['_id']), additional_claims=claims)
            refresh_token = create_refresh_token(identity=str(user['_id']), additional_claims=claims)
            
            # Extraer JTI del refresh token para la sesión
            from flask import current_app
            import jwt
            secret = current_app.config['JWT_SECRET_KEY']
            algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
            decoded_refresh = jwt.decode(refresh_token, secret, algorithms=[algorithm])
            refresh_token_jti = decoded_refresh.get('jti')
            
            # Crear sesión en base de datos
            session_result = self.session_service.create_user_session(
                user_id=str(user['_id']),
                refresh_token_jti=refresh_token_jti,
                request_data=request_data
            )
            
            if not session_result['success']:
                return {'success': False, 'errors': ['Error creando sesión']}
            
            # Aplicar límite de sesiones por usuario (máximo 5)
            self.session_service.enforce_max_sessions_per_user(str(user['_id']), max_sessions=5)
            
            # Registrar último inicio de sesión
            self.db[collection].update_one({'_id': user['_id']}, {'$set': {'last_login': datetime.utcnow()}})
            user_data = {
                'id': str(user['_id']),
                'email': user.get('email'),
                'username': user.get('username') or user.get('usuario'),
                'role': role,
                'permisos': user_perms,
                'is_super_admin': role == 'super_admin'
            }
            return {
                'success': True, 
                'access_token': access_token,
                'refresh_token': refresh_token,
                'data': user_data
            }
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}

    def refresh_token(self, refresh_token, request_data=None):
        """Genera un nuevo access token usando un refresh token válido"""
        try:
            from flask import current_app
            import jwt
            
            # Decodificar el refresh token manualmente para verificar que sea válido
            secret = current_app.config['JWT_SECRET_KEY']
            algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
            
            decoded_token = jwt.decode(
                refresh_token, 
                secret, 
                algorithms=[algorithm],
                options={"verify_exp": True}  # Verificar expiración
            )
            
            # Flask-JWT-Extended usa 'type' para distinguir access de refresh
            token_type = decoded_token.get('type')
            if token_type != 'refresh':
                return {'success': False, 'errors': [f'Token inválido - tipo: {token_type}, esperado: refresh']}
            
            user_id = decoded_token.get('sub')
            role = decoded_token.get('role')
            refresh_token_jti = decoded_token.get('jti')
            
            if not user_id or not role or not refresh_token_jti:
                return {'success': False, 'errors': ['Refresh token inválido']}
            
            # VALIDAR SESIÓN EN BASE DE DATOS
            session_validation = self.session_service.validate_refresh_token_session(
                refresh_token_jti=refresh_token_jti,
                request_data=request_data
            )
            
            if not session_validation['success']:
                return {'success': False, 'errors': ['Sesión inválida o expirada']}
            
            # Verificar que el usuario aún existe y está activo
            collection = 'administradores' if role in ['super_admin', 'admin'] else 'empresas'
            user = self.db[collection].find_one({'_id': ObjectId(user_id)})
            
            if not user:
                # Si el usuario no existe, invalidar la sesión
                self.session_service.invalidate_session(refresh_token_jti=refresh_token_jti)
                return {'success': False, 'errors': ['Usuario no encontrado']}
            
            is_active = user.get('activo') if collection == 'administradores' else user.get('activa', True)
            if is_active is None:
                is_active = user.get('is_active', True)
            if not is_active:
                # Si el usuario está inactivo, invalidar la sesión
                self.session_service.invalidate_session(refresh_token_jti=refresh_token_jti)
                return {'success': False, 'errors': ['Usuario inactivo']}
            
            # Generar nuevo access token con la misma información
            claims = {'role': role}
            new_access_token = create_access_token(identity=user_id, additional_claims=claims)
            
            # Actualizar última actividad del usuario
            self.db[collection].update_one(
                {'_id': user['_id']}, 
                {'$set': {'last_activity': datetime.utcnow()}}
            )
            
            # Nota: La sesión ya se actualizó automáticamente en validate_refresh_token_session
            
            return {
                'success': True,
                'access_token': new_access_token
            }
            
        except jwt.ExpiredSignatureError:
            return {'success': False, 'errors': ['Refresh token expirado']}
        except jwt.InvalidTokenError:
            return {'success': False, 'errors': ['Refresh token inválido']}
        except Exception as e:
            return {'success': False, 'errors': [f'Error procesando refresh token: {str(e)}']}
    
    def logout(self, refresh_token):
        """Invalidar sesión específica"""
        try:
            from flask import current_app
            import jwt
            
            # Extraer JTI del refresh token
            secret = current_app.config['JWT_SECRET_KEY']
            algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
            
            decoded_token = jwt.decode(
                refresh_token, 
                secret, 
                algorithms=[algorithm],
                options={"verify_exp": False}  # No verificar expiración para logout
            )
            
            refresh_token_jti = decoded_token.get('jti')
            
            if not refresh_token_jti:
                return {'success': False, 'errors': ['Token inválido']}
            
            # Invalidar sesión en base de datos
            result = self.session_service.logout_user_session(refresh_token_jti)
            
            return result
            
        except Exception as e:
            # Aunque falle, consideramos el logout exitoso
            return {'success': True, 'message': 'Sesión cerrada'}
    
    def logout_all_sessions(self, user_id, keep_current_jti=None):
        """Cerrar todas las sesiones de un usuario"""
        try:
            result = self.session_service.logout_all_user_sessions(
                user_id=user_id,
                keep_current_jti=keep_current_jti
            )
            return result
        except Exception as e:
            return {'success': False, 'errors': [f'Error cerrando sesiones: {str(e)}']}
    
    def get_user_sessions(self, user_id):
        """Obtener sesiones activas de un usuario"""
        try:
            return self.session_service.get_user_active_sessions(user_id)
        except Exception as e:
            return {'success': False, 'errors': [f'Error obteniendo sesiones: {str(e)}']}
