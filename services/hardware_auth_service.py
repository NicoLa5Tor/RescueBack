import jwt
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any
from core.database import Database
from bson import ObjectId


class HardwareAuthService:
    """
    Servicio simple para autenticación de hardware.
    Valida hardware existe y coincide con el tópico guardado.
    """
    
    def __init__(self):
        self.db_instance = Database()
        self.db = self.db_instance.get_database()
        self.secret_key = "hardware_auth_secret_key_2024"  # En producción usar variable de entorno
        self.token_expiry_minutes = 5
        self.used_tokens_collection = self.db.used_hardware_tokens  # Colección para tokens usados
    
    def authenticate_hardware(self, empresa_nombre: str, sede_nombre: str, tipo_hardware: str, hardware_nombre: str) -> Dict[str, Any]:
        """
        Autenticación simple de hardware.
        1. Verifica que el hardware existe
        2. Verifica que el tópico empresa/sede/TIPO_HARDWARE/nombre coincide con el guardado
        
        Args:
            empresa_nombre: Nombre de la empresa
            sede_nombre: Nombre de la sede
            tipo_hardware: Tipo de hardware (se convierte a mayúsculas)
            hardware_nombre: Nombre del hardware
            
        Returns:
            Dict con success=True/False y token si es exitosa
        """
        try:
            # Normalizar tipo de hardware a mayúsculas
            tipo_hardware_normalizado = tipo_hardware.strip().upper()
            
            # print(f"🔐 AUTENTICACIÓN SIMPLE DE HARDWARE")
            # print(f"   Hardware: {hardware_nombre}")
            # print(f"   Tipo Hardware: {tipo_hardware_normalizado}")
            # print(f"   Tópico: {empresa_nombre}/{sede_nombre}/{tipo_hardware_normalizado}/{hardware_nombre}")
            
            # PASO 1: Verificar que el hardware existe
            # Buscar por nombre exacto primero; si no encuentra, hacer búsqueda normalizada
            hardware_nombre_normalizado = hardware_nombre.strip().replace(' ', '')

            hardware = self.db.hardware.find_one({
                'nombre': hardware_nombre,
                'activa': True
            })

            if not hardware:
                # Fallback: búsqueda por nombre sin espacios (nombres con espacios en DB)
                hardware_cursor = self.db.hardware.find(
                    {'activa': True, 'nombre': {'$regex': f'^.{{1,100}}$'}},
                    {'nombre': 1, 'topic': 1}
                )
                for hw in hardware_cursor:
                    if hw.get('nombre', '').strip().replace(' ', '') == hardware_nombre_normalizado:
                        hardware = self.db.hardware.find_one({'_id': hw['_id']})
                        break
            
            if not hardware:
                return {
                    'success': False,
                    'error': 'Credenciales inválidas',
                    'message': 'Las credenciales de hardware no son válidas'
                }
            
            # print(f"✅ Hardware encontrado: {hardware['nombre']}")
            
            # PASO 2: Verificar que el tópico coincide con el guardado
            topico_recibido = f"{empresa_nombre}/{sede_nombre}/{tipo_hardware_normalizado}/{hardware_nombre}"
            topico_guardado = hardware.get('topic', '')

            if topico_recibido != topico_guardado:
                import logging as _logging
                _logging.getLogger(__name__).warning(
                    "Topic mismatch hardware=%s recibido=%r guardado=%r",
                    hardware_nombre, topico_recibido, topico_guardado
                )
                return {
                    'success': False,
                    'error': 'Credenciales inválidas',
                    'message': 'Las credenciales de hardware no son válidas'
                }
            
            # print(f"✅ Tópico verificado: {topico_guardado}")
            
            # PASO 3: Generar token con información básica + hardware_id
            current_time = datetime.utcnow()
            expiry_time = current_time + timedelta(minutes=self.token_expiry_minutes)
            
            payload = {
                'hardware_id': str(hardware['_id']),
                'hardware_nombre': hardware['nombre'],
                'topico': topico_guardado,
                'issued_at': current_time.timestamp(),
                'expires_at': expiry_time.timestamp(),
                'token_type': 'hardware_auth'
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')
            
            # print(f"✅ Token generado para {self.token_expiry_minutes} minutos")
            
            return {
                'success': True,
                'token': token,
                'hardware_id': str(hardware['_id']),
                'topico': topico_guardado
            }
            
        except Exception as e:
            # print(f"💥 ERROR: {str(e)}")
            return {
                'success': False,
                'error': 'Error interno',
                'message': f'Error durante la autenticación: {str(e)}'
            }
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verifica un token de hardware y retorna información del payload.
        
        Args:
            token: Token JWT a verificar
            
        Returns:
            Dict con success=True/False y payload si es válido
        """
        try:
            # print(f"🔍 VERIFICANDO TOKEN DE HARDWARE")
            
            # Decodificar el token
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Verificar que es un token de hardware
            if payload.get('token_type') != 'hardware_auth':
                return {
                    'success': False,
                    'error': 'Tipo de token inválido',
                    'message': 'El token no es de tipo hardware_auth'
                }
            
            # Verificar que el token no ha sido usado previamente
            token_hash = self._get_token_hash(token)
            if self._is_token_used(token_hash):
                return {
                    'success': False,
                    'error': 'Token inválido',
                    'message': 'El token de hardware ya ha sido utilizado'
                }
            
            # Verificar que no ha expirado
            current_time = datetime.utcnow().timestamp()
            expires_at = payload.get('expires_at', 0)
            
            if current_time > expires_at:
                return {
                    'success': False,
                    'error': 'Token expirado',
                    'message': 'El token de hardware ha expirado'
                }
            
            # Verificar que el hardware aún existe y está activo
            hardware_id = payload.get('hardware_id')
            if hardware_id:
                hardware = self.db.hardware.find_one({
                    '_id': ObjectId(hardware_id),
                    'activa': True
                })
                
                if not hardware:
                    return {
                        'success': False,
                        'error': 'Hardware no válido',
                        'message': 'El hardware asociado al token no existe o está inactivo'
                    }
            
            # print(f"✅ Token verificado correctamente para hardware: {payload.get('hardware_nombre')}")
            
            return {
                'success': True,
                'payload': payload,
                'message': 'Token válido'
            }
            
        except jwt.ExpiredSignatureError:
            return {
                'success': False,
                'error': 'Token expirado',
                'message': 'El token de hardware ha expirado'
            }
        except jwt.InvalidTokenError:
            return {
                'success': False,
                'error': 'Token inválido',
                'message': 'El token de hardware no es válido'
            }
        except Exception as e:
            # print(f"💥 ERROR verificando token: {str(e)}")
            return {
                'success': False,
                'error': 'Error interno',
                'message': f'Error verificando token: {str(e)}'
            }
    
    def invalidate_token_after_use(self, token: str) -> bool:
        """
        Invalida un token después de su uso para evitar reutilización.
        
        Args:
            token: Token JWT a invalidar
            
        Returns:
            bool: True si se invalidó correctamente, False en caso de error
        """
        try:
            token_hash = self._get_token_hash(token)
            
            # Decodificar para obtener información del token
            try:
                payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
                hardware_id = payload.get('hardware_id')
                expires_at = payload.get('expires_at')
            except:
                # Si no se puede decodificar, igual lo agregamos a la blacklist
                hardware_id = None
                expires_at = None
            
            # Registrar el token como usado
            used_token_doc = {
                'token_hash': token_hash,
                'hardware_id': hardware_id,
                'used_at': datetime.utcnow(),
                'expires_at': datetime.fromtimestamp(expires_at) if expires_at else None
            }
            
            self.used_tokens_collection.insert_one(used_token_doc)
            # print(f"🚫 Token invalidado después de uso para hardware: {payload.get('hardware_nombre') if 'payload' in locals() else 'desconocido'}")
            
            return True
            
        except Exception as e:
            # print(f"💥 ERROR invalidando token: {str(e)}")
            return False
    
    def _get_token_hash(self, token: str) -> str:
        """
        Genera un hash del token para almacenamiento seguro.
        
        Args:
            token: Token JWT
            
        Returns:
            str: Hash SHA256 del token
        """
        return hashlib.sha256(token.encode()).hexdigest()
    
    def _is_token_used(self, token_hash: str) -> bool:
        """
        Verifica si un token ya ha sido usado.
        
        Args:
            token_hash: Hash del token a verificar
            
        Returns:
            bool: True si el token ya fue usado, False en caso contrario
        """
        try:
            used_token = self.used_tokens_collection.find_one({
                'token_hash': token_hash
            })
            
            return used_token is not None
            
        except Exception as e:
            # print(f"💥 ERROR verificando si token fue usado: {str(e)}")
            # En caso de error, asumir que no fue usado para no bloquear innecesariamente
            return False
    
    def cleanup_expired_tokens(self) -> int:
        """
        Limpia tokens expirados de la blacklist para mantener la colección pequeña.
        
        Returns:
            int: Número de tokens limpiados
        """
        try:
            current_time = datetime.utcnow()
            
            # Eliminar tokens que ya expiraron hace más de 1 hora
            result = self.used_tokens_collection.delete_many({
                'expires_at': {
                    '$lt': current_time - timedelta(hours=1)
                }
            })
            
            if result.deleted_count > 0:
                # print(f"🧩 Limpiados {result.deleted_count} tokens expirados de la blacklist")
                pass
            
            return result.deleted_count
            
        except Exception as e:
            # print(f"💥 ERROR limpiando tokens expirados: {str(e)}")
            return 0
