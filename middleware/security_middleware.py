import hashlib
import time
from flask import request, jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity
from core.database import Database

class SecurityMiddleware:
    def __init__(self):
        self.db = Database().get_database()
    
    def get_client_fingerprint(self, request):
        """
        Crea una huella digital única del cliente basada en:
        - IP Address
        - User-Agent
        - Accept headers
        """
        ip = request.remote_addr or 'unknown'
        user_agent = request.headers.get('User-Agent', 'unknown')
        accept = request.headers.get('Accept', 'unknown')
        
        # Crear hash único
        fingerprint_data = f"{ip}:{user_agent}:{accept}"
        fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()
        
        return fingerprint
    
    def validate_token_binding(self, user_id, current_fingerprint):
        """
        Valida que el token esté vinculado al cliente original
        """
        try:
            # Buscar sesión activa
            session = self.db.user_sessions.find_one({
                'user_id': user_id,
                'is_active': True
            })
            
            if not session:
                return False
            
            # Verificar huella digital
            if session.get('fingerprint') != current_fingerprint:
                # Token está siendo usado desde otro dispositivo/navegador
                return False
            
            # Verificar tiempo de última actividad (para detectar uso simultáneo)
            last_activity = session.get('last_activity')
            if last_activity:
                time_diff = time.time() - last_activity
                # Si la última actividad fue hace más de 10 minutos, actualizar
                if time_diff > 600:  # 10 minutos
                    self.db.user_sessions.update_one(
                        {'_id': session['_id']},
                        {'$set': {'last_activity': time.time()}}
                    )
            
            return True
            
        except Exception as e:
            # print(f"Error validando token binding: {str(e)}")
            return False
    
    def create_session_record(self, user_id, fingerprint, jti):
        """
        Crea un registro de sesión vinculado al token
        """
        try:
            # Invalidar sesiones anteriores del mismo usuario
            self.db.user_sessions.update_many(
                {'user_id': user_id},
                {'$set': {'is_active': False}}
            )
            
            # Crear nueva sesión
            session_data = {
                'user_id': user_id,
                'fingerprint': fingerprint,
                'jti': jti,  # JWT ID único
                'created_at': time.time(),
                'last_activity': time.time(),
                'is_active': True
            }
            
            self.db.user_sessions.insert_one(session_data)
            return True
            
        except Exception as e:
            # print(f"Error creando registro de sesión: {str(e)}")
            return False
    
    def invalidate_session(self, user_id, jti=None):
        """
        Invalida sesiones del usuario
        """
        try:
            query = {'user_id': user_id}
            if jti:
                query['jti'] = jti
            
            self.db.user_sessions.update_many(
                query,
                {'$set': {'is_active': False}}
            )
            return True
            
        except Exception as e:
            # print(f"Error invalidando sesión: {str(e)}")
            return False
    
    def validate_request_security(self):
        """
        Middleware principal de validación de seguridad
        """
        try:
            # Obtener datos del JWT
            jwt_data = get_jwt()
            user_id = get_jwt_identity()
            jti = jwt_data.get('jti')
            
            if not user_id or not jti:
                return jsonify({'error': 'Token inválido'}), 401
            
            # Obtener huella digital del cliente actual
            current_fingerprint = self.get_client_fingerprint(request)
            
            # Validar vinculación del token
            if not self.validate_token_binding(user_id, current_fingerprint):
                # Token está siendo usado desde otro dispositivo
                return jsonify({'error': 'Token comprometido - sesión invalidada'}), 401
            
            return None  # Todo correcto
            
        except Exception as e:
            # print(f"Error en validación de seguridad: {str(e)}")
            return jsonify({'error': 'Error de seguridad'}), 500
