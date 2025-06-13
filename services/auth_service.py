import jwt
from datetime import datetime, timedelta
from utils.security import verify_password
from config import Config
from repositories.auth_repository import AuthRepository
class AuthService:
    def __init__(self):
        self.auth_repository = AuthRepository()
        self.config = Config()
    
    def login(self, email_or_usuario, password):
        """
        Servicio de login que autentica administradores y empresas
        Retorna JWT token si las credenciales son válidas
        """
        try:
            # 1. Intentar autenticar como administrador primero
            admin_result = self._authenticate_admin(email_or_usuario, password)
            if admin_result['success']:
                return admin_result
            
            # 2. Si no es admin, intentar autenticar como empresa
            empresa_result = self._authenticate_empresa(email_or_usuario, password)
            if empresa_result['success']:
                return empresa_result
            
            # 3. Si ninguno funciona, credenciales inválidas
            return {
                'success': False,
                'access': False,
                'message': 'Credenciales inválidas',
                'errors': ['Usuario/email o contraseña incorrectos']
            }
            
        except Exception as e:
            return {
                'success': False,
                'access': False,
                'message': 'Error en el servidor',
                'errors': [str(e)]
            }
    
    def _authenticate_admin(self, email_or_usuario, password):
        """Autentica un administrador"""
        try:
            # Buscar admin por usuario o email
            admin = None
            if '@' in email_or_usuario:
                admin = self.auth_repository.find_admin_by_email(email_or_usuario)
            else:
                admin = self.auth_repository.find_admin_by_usuario(email_or_usuario)
            
            if not admin:
                return {'success': False}
            
            # Verificar contraseña
            if not admin.verify_password(password):
                return {'success': False}
            
            # Actualizar último login
            self.auth_repository.update_admin_login(admin._id)
            
            # Generar JWT token
            token = self._generate_token({
                'user_id': str(admin._id),
                'usuario': admin.usuario,
                'nombre': admin.nombre,
                'email': admin.email,
                'rol': admin.rol,
                'tipo': 'admin'
            })
            
            return {
                'success': True,
                'access': True,
                'message': 'Login exitoso',
                'token': token,
                'user': {
                    'id': str(admin._id),
                    'usuario': admin.usuario,
                    'nombre': admin.nombre,
                    'email': admin.email,
                    'rol': admin.rol,
                    'tipo': 'admin',
                    'permisos': self.config.PERMISSIONS.get(admin.rol, [])
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _authenticate_empresa(self, email, password):
        """Autentica una empresa"""
        try:
            # Buscar empresa por email
            empresa = self.auth_repository.find_empresa_by_email(email)
            
            if not empresa:
                return {'success': False}
            
            # Verificar contraseña (asumiendo que la empresa tiene campo 'password_hash')
            if 'password_hash' not in empresa:
                return {'success': False}

            if not verify_password(password, empresa['password_hash']):
                return {'success': False}
            
            # Actualizar último login
            self.auth_repository.update_empresa_login(empresa['_id'])
            
            # Generar JWT token
            token = self._generate_token({
                'user_id': str(empresa['_id']),
                'empresa_id': str(empresa['_id']),
                'nombre': empresa['nombre'],
                'email': empresa.get('email'),
                'rol': 'empresa',
                'tipo': 'empresa'
            })
            
            return {
                'success': True,
                'access': True,
                'message': 'Login exitoso',
                'token': token,
                'user': {
                    'id': str(empresa['_id']),
                    'empresa_id': str(empresa['_id']),
                    'nombre': empresa['nombre'],
                    'email': empresa.get('email'),
                    'rol': 'empresa',
                    'tipo': 'empresa',
                    'permisos': self.config.PERMISSIONS.get('empresa', [])
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _generate_token(self, payload):
        """Genera un JWT token"""
        try:
            # Agregar información de expiración
            payload['exp'] = datetime.utcnow() + self.config.JWT_EXPIRATION_DELTA
            payload['iat'] = datetime.utcnow()
            
            # Generar el token
            token = jwt.encode(
                payload,
                self.config.JWT_SECRET_KEY,
                algorithm=self.config.JWT_ALGORITHM
            )
            
            return token
            
        except Exception as e:
            raise Exception(f"Error generando token: {str(e)}")
    
    def verify_token(self, token):
        """Verifica y decodifica un JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.config.JWT_SECRET_KEY,
                algorithms=[self.config.JWT_ALGORITHM]
            )
            
            # Verificar que el usuario/empresa todavía existe y está activo
            if payload['tipo'] == 'admin':
                user = self.auth_repository.find_admin_by_id(payload['user_id'])
                if not user:
                    return {'valid': False, 'error': 'Usuario no encontrado'}
            elif payload['tipo'] == 'empresa':
                user = self.auth_repository.find_empresa_by_id(payload['user_id'])
                if not user:
                    return {'valid': False, 'error': 'Empresa no encontrada'}
            
            return {
                'valid': True,
                'payload': payload,
                'user_id': payload['user_id'],
                'rol': payload['rol'],
                'tipo': payload['tipo'],
                'permisos': self.config.PERMISSIONS.get(payload['rol'], [])
            }
            
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token expirado'}
        except jwt.InvalidTokenError:
            return {'valid': False, 'error': 'Token inválido'}
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def check_permission(self, token_payload, required_permission):
        """Verifica si un usuario tiene un permiso específico"""
        try:
            user_permissions = self.config.PERMISSIONS.get(token_payload['rol'], [])
            return required_permission in user_permissions
        except:
            return False
    
    def refresh_token(self, token):
        """Renueva un token JWT válido"""
        try:
            verification = self.verify_token(token)
            if not verification['valid']:
                return {
                    'success': False,
                    'message': 'Token inválido para renovar'
                }
            
            # Crear nuevo token con la misma información
            payload = verification['payload'].copy()
            payload.pop('exp', None)  # Remover expiración anterior
            payload.pop('iat', None)  # Remover timestamp anterior
            
            new_token = self._generate_token(payload)
            
            return {
                'success': True,
                'token': new_token,
                'message': 'Token renovado exitosamente'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': 'Error renovando token',
                'errors': [str(e)]
            }
    
    def login(self, email_or_usuario, password):
        """
        Servicio de login que autentica administradores y empresas
        Retorna JWT token si las credenciales son válidas
        """
        try:
            # 1. Intentar autenticar como administrador primero
            admin_result = self._authenticate_admin(email_or_usuario, password)
            if admin_result['success']:
                return admin_result
            
            # 2. Si no es admin, intentar autenticar como empresa
            empresa_result = self._authenticate_empresa(email_or_usuario, password)
            if empresa_result['success']:
                return empresa_result
            
            # 3. Si ninguno funciona, credenciales inválidas
            return {
                'success': False,
                'access': False,
                'message': 'Credenciales inválidas',
                'errors': ['Usuario/email o contraseña incorrectos']
            }
            
        except Exception as e:
            return {
                'success': False,
                'access': False,
                'message': 'Error en el servidor',
                'errors': [str(e)]
            }
    
    def _authenticate_admin(self, email_or_usuario, password):
        """Autentica un administrador"""
        try:
            # Buscar admin por usuario o email
            admin = None
            if '@' in email_or_usuario:
                admin = self.auth_repository.find_admin_by_email(email_or_usuario)
            else:
                admin = self.auth_repository.find_admin_by_usuario(email_or_usuario)
            
            if not admin:
                return {'success': False}
            
            # Verificar contraseña
            if not admin.verify_password(password):
                return {'success': False}
            
            # Actualizar último login
            self.auth_repository.update_admin_login(admin._id)
            
            # Generar JWT token
            token = self._generate_token({
                'user_id': str(admin._id),
                'usuario': admin.usuario,
                'nombre': admin.nombre,
                'email': admin.email,
                'rol': admin.rol,
                'tipo': 'admin'
            })
            
            return {
                'success': True,
                'access': True,
                'message': 'Login exitoso',
                'token': token,
                'user': {
                    'id': str(admin._id),
                    'usuario': admin.usuario,
                    'nombre': admin.nombre,
                    'email': admin.email,
                    'rol': admin.rol,
                    'tipo': 'admin',
                    'permisos': self.config.PERMISSIONS.get(admin.rol, [])
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _authenticate_empresa(self, email, password):
        """Autentica una empresa"""
        try:
            # Buscar empresa por email
            empresa = self.auth_repository.find_empresa_by_email(email)
            
            if not empresa:
                return {'success': False}
            
            # Verificar contraseña (asumiendo que la empresa tiene campo 'password_hash')
            if 'password_hash' not in empresa:
                return {'success': False}

            if not verify_password(password, empresa['password_hash']):
                return {'success': False}
            
            # Actualizar último login
            self.auth_repository.update_empresa_login(empresa['_id'])
            
            # Generar JWT token
            token = self._generate_token({
                'user_id': str(empresa['_id']),
                'empresa_id': str(empresa['_id']),
                'nombre': empresa['nombre'],
                'email': empresa.get('email'),
                'rol': 'empresa',
                'tipo': 'empresa'
            })
            
            return {
                'success': True,
                'access': True,
                'message': 'Login exitoso',
                'token': token,
                'user': {
                    'id': str(empresa['_id']),
                    'empresa_id': str(empresa['_id']),
                    'nombre': empresa['nombre'],
                    'email': empresa.get('email'),
                    'rol': 'empresa',
                    'tipo': 'empresa',
                    'permisos': self.config.PERMISSIONS.get('empresa', [])
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _generate_token(self, payload):
        """Genera un JWT token"""
        try:
            # Agregar información de expiración
            payload['exp'] = datetime.utcnow() + self.config.JWT_EXPIRATION_DELTA
            payload['iat'] = datetime.utcnow()
            
            # Generar el token
            token = jwt.encode(
                payload,
                self.config.JWT_SECRET_KEY,
                algorithm=self.config.JWT_ALGORITHM
            )
            
            return token
            
        except Exception as e:
            raise Exception(f"Error generando token: {str(e)}")
    
    def verify_token(self, token):
        """Verifica y decodifica un JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.config.JWT_SECRET_KEY,
                algorithms=[self.config.JWT_ALGORITHM]
            )
            
            # Verificar que el usuario/empresa todavía existe y está activo
            if payload['tipo'] == 'admin':
                user = self.auth_repository.find_admin_by_id(payload['user_id'])
                if not user:
                    return {'valid': False, 'error': 'Usuario no encontrado'}
            elif payload['tipo'] == 'empresa':
                user = self.auth_repository.find_empresa_by_id(payload['user_id'])
                if not user:
                    return {'valid': False, 'error': 'Empresa no encontrada'}
            
            return {
                'valid': True,
                'payload': payload,
                'user_id': payload['user_id'],
                'rol': payload['rol'],
                'tipo': payload['tipo'],
                'permisos': self.config.PERMISSIONS.get(payload['rol'], [])
            }
            
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token expirado'}
        except jwt.InvalidTokenError:
            return {'valid': False, 'error': 'Token inválido'}
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def check_permission(self, token_payload, required_permission):
        """Verifica si un usuario tiene un permiso específico"""
        try:
            user_permissions = self.config.PERMISSIONS.get(token_payload['rol'], [])
            return required_permission in user_permissions
        except:
            return False
    
    def refresh_token(self, token):
        """Renueva un token JWT válido"""
        try:
            verification = self.verify_token(token)
            if not verification['valid']:
                return {
                    'success': False,
                    'message': 'Token inválido para renovar'
                }
            
            # Crear nuevo token con la misma información
            payload = verification['payload'].copy()
            payload.pop('exp', None)  # Remover expiración anterior
            payload.pop('iat', None)  # Remover timestamp anterior
            
            new_token = self._generate_token(payload)
            
            return {
                'success': True,
                'token': new_token,
                'message': 'Token renovado exitosamente'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': 'Error renovando token',
                'errors': [str(e)]
            }