import jwt
import time
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from database import Database
from bson import ObjectId


class HardwareAuthService:
    """
    Servicio para autenticación y autorización temporal de hardware.
    Principios SOLID aplicados:
    - Single Responsibility: Solo maneja autenticación de hardware
    - Open/Closed: Extensible para nuevos tipos de validación
    - Liskov Substitution: Puede ser reemplazado por otra implementación
    - Interface Segregation: Interfaces específicas para cada funcionalidad
    - Dependency Inversion: Depende de abstracciones (Database)
    """
    
    def __init__(self):
        self.db = Database()
        self.secret_key = "hardware_auth_secret_key_2024"  # En producción usar variable de entorno
        self.token_expiry_minutes = 5  # 5 minutos como solicitaste
        
    def authenticate_hardware(self, hardware_nombre: str, empresa_nombre: str, sede: str) -> Dict[str, Any]:
        """
        Endpoint único que valida hardware, empresa y sede, y genera token temporal.
        
        Args:
            hardware_nombre: Nombre del hardware a autenticar
            empresa_nombre: Nombre de la empresa
            sede: Nombre de la sede
            
        Returns:
            Dict con resultado de autenticación y token si es exitosa
        """
        try:
            # Paso 1: Validar que todos los parámetros estén presentes
            validation_result = self._validate_input_parameters(hardware_nombre, empresa_nombre, sede)
            if not validation_result['success']:
                return validation_result
            
            # Paso 2: Verificar empresa
            empresa_result = self._verify_empresa(empresa_nombre)
            if not empresa_result['success']:
                return empresa_result
            
            empresa_data = empresa_result['data']
            
            # Paso 3: Verificar sede
            sede_result = self._verify_sede(empresa_data['_id'], sede)
            if not sede_result['success']:
                return sede_result
            
            # Paso 4: Verificar hardware
            hardware_result = self._verify_hardware(hardware_nombre, empresa_data['_id'])
            if not hardware_result['success']:
                return hardware_result
            
            hardware_data = hardware_result['data']
            
            # Paso 5: Generar token temporal
            token_result = self._generate_temporal_token(hardware_data, empresa_data, sede)
            if not token_result['success']:
                return token_result
            
            # Paso 6: Registrar sesión de autenticación
            self._log_authentication_session(hardware_data, empresa_data, sede)
            
            return {
                'success': True,
                'message': 'Autenticación exitosa',
                'data': {
                    'hardware_id': str(hardware_data['_id']),
                    'hardware_nombre': hardware_data['nombre'],
                    'empresa_id': str(empresa_data['_id']),
                    'empresa_nombre': empresa_data['nombre'],
                    'sede': sede,
                    'token': token_result['token'],
                    'expires_at': token_result['expires_at'],
                    'valid_for_minutes': self.token_expiry_minutes
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'Error interno en autenticación',
                'message': f'Ha ocurrido un error inesperado: {str(e)}'
            }
    
    def _validate_input_parameters(self, hardware_nombre: str, empresa_nombre: str, sede: str) -> Dict[str, Any]:
        """Valida que todos los parámetros de entrada estén presentes y sean válidos"""
        if not hardware_nombre or not hardware_nombre.strip():
            return {
                'success': False,
                'error': 'Parámetro faltante',
                'message': 'El nombre del hardware es requerido'
            }
        
        if not empresa_nombre or not empresa_nombre.strip():
            return {
                'success': False,
                'error': 'Parámetro faltante',
                'message': 'El nombre de la empresa es requerido'
            }
        
        if not sede or not sede.strip():
            return {
                'success': False,
                'error': 'Parámetro faltante',
                'message': 'El nombre de la sede es requerido'
            }
        
        return {'success': True}
    
    def _verify_empresa(self, empresa_nombre: str) -> Dict[str, Any]:
        """Verifica que la empresa exista y esté activa"""
        try:
            empresa = self.db.empresas.find_one({
                'nombre': empresa_nombre,
                'activa': True
            })
            
            if not empresa:
                return {
                    'success': False,
                    'error': 'Empresa no encontrada',
                    'message': f'La empresa "{empresa_nombre}" no existe o está inactiva'
                }
            
            return {
                'success': True,
                'data': empresa
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'Error de base de datos',
                'message': f'Error al verificar empresa: {str(e)}'
            }
    
    def _verify_sede(self, empresa_id: ObjectId, sede: str) -> Dict[str, Any]:
        """Verifica que la sede exista en la empresa"""
        try:
            empresa = self.db.empresas.find_one({
                '_id': empresa_id,
                'sedes': {'$in': [sede]}
            })
            
            if not empresa:
                return {
                    'success': False,
                    'error': 'Sede no encontrada',
                    'message': f'La sede "{sede}" no existe en la empresa especificada'
                }
            
            return {'success': True}
            
        except Exception as e:
            return {
                'success': False,
                'error': 'Error de base de datos',
                'message': f'Error al verificar sede: {str(e)}'
            }
    
    def _verify_hardware(self, hardware_nombre: str, empresa_id: ObjectId) -> Dict[str, Any]:
        """Verifica que el hardware exista, esté activo y pertenezca a la empresa"""
        try:
            hardware = self.db.hardware.find_one({
                'nombre': hardware_nombre,
                'empresa_id': empresa_id,
                'activo': True
            })
            
            if not hardware:
                return {
                    'success': False,
                    'error': 'Hardware no encontrado',
                    'message': f'El hardware "{hardware_nombre}" no existe, está inactivo o no pertenece a la empresa especificada'
                }
            
            return {
                'success': True,
                'data': hardware
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'Error de base de datos',
                'message': f'Error al verificar hardware: {str(e)}'
            }
    
    def _generate_temporal_token(self, hardware_data: Dict, empresa_data: Dict, sede: str) -> Dict[str, Any]:
        """Genera un token temporal JWT para autorizar envío de alertas"""
        try:
            current_time = datetime.utcnow()
            expiry_time = current_time + timedelta(minutes=self.token_expiry_minutes)
            
            # Payload del token
            payload = {
                'hardware_id': str(hardware_data['_id']),
                'hardware_nombre': hardware_data['nombre'],
                'empresa_id': str(empresa_data['_id']),
                'empresa_nombre': empresa_data['nombre'],
                'sede': sede,
                'issued_at': current_time.timestamp(),
                'expires_at': expiry_time.timestamp(),
                'token_type': 'hardware_auth'
            }
            
            # Generar token JWT
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')
            
            return {
                'success': True,
                'token': token,
                'expires_at': expiry_time.isoformat(),
                'payload': payload
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'Error generando token',
                'message': f'No se pudo generar el token: {str(e)}'
            }
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verifica si un token es válido y no ha expirado"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Verificar expiración
            if payload['expires_at'] < time.time():
                return {
                    'success': False,
                    'error': 'Token expirado',
                    'message': 'El token ha expirado, solicite uno nuevo'
                }
            
            # Verificar que es un token de hardware
            if payload.get('token_type') != 'hardware_auth':
                return {
                    'success': False,
                    'error': 'Token inválido',
                    'message': 'El token no es del tipo correcto'
                }
            
            return {
                'success': True,
                'payload': payload
            }
            
        except jwt.ExpiredSignatureError:
            return {
                'success': False,
                'error': 'Token expirado',
                'message': 'El token ha expirado'
            }
        except jwt.InvalidTokenError:
            return {
                'success': False,
                'error': 'Token inválido',
                'message': 'El token es inválido'
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'Error verificando token',
                'message': f'Error al verificar token: {str(e)}'
            }
    
    def _log_authentication_session(self, hardware_data: Dict, empresa_data: Dict, sede: str):
        """Registra la sesión de autenticación en la base de datos"""
        try:
            session_log = {
                'hardware_id': hardware_data['_id'],
                'hardware_nombre': hardware_data['nombre'],
                'empresa_id': empresa_data['_id'],
                'empresa_nombre': empresa_data['nombre'],
                'sede': sede,
                'authenticated_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(minutes=self.token_expiry_minutes),
                'session_type': 'hardware_auth'
            }
            
            # Crear colección si no existe
            self.db.hardware_auth_sessions.insert_one(session_log)
            
        except Exception as e:
            # El logging es opcional, no debe fallar la autenticación
            print(f"Warning: No se pudo registrar sesión de autenticación: {str(e)}")
    
    def get_active_sessions(self, hardware_id: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene las sesiones activas de autenticación"""
        try:
            query = {
                'expires_at': {'$gt': datetime.utcnow()}
            }
            
            if hardware_id:
                query['hardware_id'] = ObjectId(hardware_id)
            
            sessions = list(self.db.hardware_auth_sessions.find(query).sort('authenticated_at', -1))
            
            # Convertir ObjectId a string para serialización
            for session in sessions:
                session['_id'] = str(session['_id'])
                session['hardware_id'] = str(session['hardware_id'])
                session['empresa_id'] = str(session['empresa_id'])
                session['authenticated_at'] = session['authenticated_at'].isoformat()
                session['expires_at'] = session['expires_at'].isoformat()
            
            return {
                'success': True,
                'data': sessions,
                'total': len(sessions)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'Error obteniendo sesiones',
                'message': f'Error al obtener sesiones activas: {str(e)}'
            }
    
    def cleanup_expired_sessions(self) -> Dict[str, Any]:
        """Limpia sesiones expiradas de la base de datos"""
        try:
            result = self.db.hardware_auth_sessions.delete_many({
                'expires_at': {'$lt': datetime.utcnow()}
            })
            
            return {
                'success': True,
                'deleted_count': result.deleted_count,
                'message': f'Se eliminaron {result.deleted_count} sesiones expiradas'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'Error limpiando sesiones',
                'message': f'Error al limpiar sesiones: {str(e)}'
            }
