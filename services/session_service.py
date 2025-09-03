from repositories.session_repository import SessionRepository
from datetime import datetime, timedelta
import hashlib
import logging

logger = logging.getLogger(__name__)

class SessionService:
    def __init__(self):
        self.session_repository = SessionRepository()
    
    def create_user_session(self, user_id, refresh_token_jti, request_data=None):
        """Crear una nueva sesión de usuario"""
        try:
            # Extraer información de la request
            ip_address = None
            user_agent = None
            fingerprint = None
            
            if request_data:
                ip_address = request_data.get('remote_addr')
                user_agent = request_data.get('user_agent')
                
                # Generar fingerprint único basado en IP + User-Agent + otros datos
                fingerprint_data = f"{ip_address}_{user_agent}_{user_id}"
                fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
            
            # Datos de la sesión
            session_data = {
                'user_id': user_id,
                'refresh_token_jti': refresh_token_jti,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'fingerprint': fingerprint,
                'expires_at': datetime.utcnow() + timedelta(days=7)  # 7 días como el refresh token
            }
            
            # Crear sesión en la base de datos
            result = self.session_repository.create_session(session_data)
            
            if result['success']:
                logger.info(f"Sesión creada para usuario {user_id} con JTI {refresh_token_jti}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error creando sesión de usuario: {str(e)}")
            return {
                'success': False,
                'errors': [f'Error creando sesión: {str(e)}']
            }
    
    def validate_refresh_token_session(self, refresh_token_jti, request_data=None):
        """Validar que el refresh token tenga una sesión activa válida"""
        try:
            # Obtener sesión por JTI
            session_result = self.session_repository.get_session_by_jti(refresh_token_jti)
            
            if not session_result['success']:
                return {
                    'success': False,
                    'errors': ['Sesión inválida o expirada']
                }
            
            session = session_result['data']
            
            # Validaciones adicionales de seguridad (opcionales)
            if request_data:
                current_ip = request_data.get('remote_addr')
                current_user_agent = request_data.get('user_agent')
                
                # Verificar cambios sospechosos (opcional - puede ser muy restrictivo)
                if current_ip and session.get('ip_address'):
                    if current_ip != session['ip_address']:
                        logger.warning(f"IP cambió en sesión {session['_id']}: {session['ip_address']} -> {current_ip}")
                        # Nota: No invalidamos automáticamente por cambio de IP (usuarios móviles)
            
            return {
                'success': True,
                'data': session,
                'message': 'Sesión válida'
            }
            
        except Exception as e:
            logger.error(f"Error validando sesión: {str(e)}")
            return {
                'success': False,
                'errors': [f'Error validando sesión: {str(e)}']
            }
    
    def get_user_active_sessions(self, user_id):
        """Obtener sesiones activas de un usuario"""
        try:
            return self.session_repository.get_active_sessions_by_user(user_id)
        except Exception as e:
            logger.error(f"Error obteniendo sesiones activas: {str(e)}")
            return {
                'success': False,
                'errors': [f'Error obteniendo sesiones: {str(e)}']
            }
    
    def invalidate_session(self, session_id=None, refresh_token_jti=None):
        """Invalidar una sesión específica"""
        try:
            result = self.session_repository.invalidate_session(
                session_id=session_id, 
                jti=refresh_token_jti
            )
            
            if result['success']:
                logger.info(f"Sesión invalidada: {session_id or refresh_token_jti}")
            
            return result
        except Exception as e:
            logger.error(f"Error invalidando sesión: {str(e)}")
            return {
                'success': False,
                'errors': [f'Error invalidando sesión: {str(e)}']
            }
    
    def logout_user_session(self, refresh_token_jti):
        """Logout: invalidar sesión específica"""
        try:
            return self.invalidate_session(refresh_token_jti=refresh_token_jti)
        except Exception as e:
            logger.error(f"Error en logout de sesión: {str(e)}")
            return {
                'success': False,
                'errors': [f'Error en logout: {str(e)}']
            }
    
    def logout_all_user_sessions(self, user_id, keep_current_jti=None):
        """Logout de todas las sesiones de un usuario"""
        try:
            result = self.session_repository.invalidate_all_user_sessions(
                user_id=user_id, 
                exclude_jti=keep_current_jti
            )
            
            if result['success']:
                logger.info(f"Todas las sesiones del usuario {user_id} invalidadas (excluido: {keep_current_jti})")
            
            return result
        except Exception as e:
            logger.error(f"Error invalidando todas las sesiones: {str(e)}")
            return {
                'success': False,
                'errors': [f'Error invalidando sesiones: {str(e)}']
            }
    
    def cleanup_expired_sessions(self):
        """Limpieza de sesiones expiradas"""
        try:
            result = self.session_repository.cleanup_expired_sessions()
            
            if result['success']:
                logger.info(f"Limpieza completada: {result['deleted_count']} sesiones eliminadas")
            
            return result
        except Exception as e:
            logger.error(f"Error en limpieza de sesiones: {str(e)}")
            return {
                'success': False,
                'errors': [f'Error en limpieza: {str(e)}']
            }
    
    def get_session_statistics(self):
        """Obtener estadísticas de sesiones del sistema"""
        try:
            return self.session_repository.get_session_stats()
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {str(e)}")
            return {
                'success': False,
                'errors': [f'Error obteniendo estadísticas: {str(e)}']
            }
    
    def enforce_max_sessions_per_user(self, user_id, max_sessions=5):
        """Limitar número máximo de sesiones por usuario"""
        try:
            # Obtener sesiones activas del usuario
            sessions_result = self.get_user_active_sessions(user_id)
            
            if not sessions_result['success']:
                return sessions_result
            
            active_sessions = sessions_result['data']
            
            # Si hay más sesiones del límite, invalidar las más antiguas
            if len(active_sessions) >= max_sessions:
                # Ordenar por last_used (las más antiguas primero)
                sessions_to_remove = sorted(active_sessions, key=lambda x: x['last_used'])[:len(active_sessions) - max_sessions + 1]
                
                invalidated_count = 0
                for session in sessions_to_remove:
                    result = self.invalidate_session(session_id=session['_id'])
                    if result['success']:
                        invalidated_count += 1
                
                logger.info(f"Usuario {user_id}: Invalidadas {invalidated_count} sesiones antiguas (límite: {max_sessions})")
                
                return {
                    'success': True,
                    'message': f'{invalidated_count} sesiones antiguas invalidadas',
                    'invalidated_count': invalidated_count
                }
            
            return {
                'success': True,
                'message': 'Límite de sesiones dentro del rango permitido',
                'invalidated_count': 0
            }
            
        except Exception as e:
            logger.error(f"Error aplicando límite de sesiones: {str(e)}")
            return {
                'success': False,
                'errors': [f'Error aplicando límite: {str(e)}']
            }