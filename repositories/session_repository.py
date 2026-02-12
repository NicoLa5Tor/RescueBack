from core.database import Database
from datetime import datetime, timedelta
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

class SessionRepository:
    def __init__(self):
        self.db = Database().get_database()
        self.collection = self.db.sessions
        
    def create_session(self, session_data):
        """Crear una nueva sesión"""
        try:
            session_data['created_at'] = datetime.utcnow()
            session_data['last_used'] = datetime.utcnow()
            session_data['active'] = True
            
            result = self.collection.insert_one(session_data)
            return {
                'success': True,
                'session_id': str(result.inserted_id)
            }
        except Exception as e:
            logger.error(f"Error creando sesión: {str(e)}")
            return {
                'success': False,
                'errors': [f'Error creando sesión: {str(e)}']
            }
    
    def get_session_by_jti(self, jti):
        """Obtener sesión por JWT ID"""
        try:
            session = self.collection.find_one({
                'refresh_token_jti': jti,
                'active': True,
                'expires_at': {'$gt': datetime.utcnow()}
            })
            
            if session:
                # Actualizar last_used
                self.collection.update_one(
                    {'_id': session['_id']},
                    {'$set': {'last_used': datetime.utcnow()}}
                )
                session['_id'] = str(session['_id'])
                return {
                    'success': True,
                    'data': session
                }
            else:
                return {
                    'success': False,
                    'errors': ['Sesión no encontrada o expirada']
                }
        except Exception as e:
            logger.error(f"Error obteniendo sesión por JTI: {str(e)}")
            return {
                'success': False,
                'errors': [f'Error obteniendo sesión: {str(e)}']
            }
    
    def get_active_sessions_by_user(self, user_id):
        """Obtener todas las sesiones activas de un usuario"""
        try:
            sessions = list(self.collection.find({
                'user_id': user_id,
                'active': True,
                'expires_at': {'$gt': datetime.utcnow()}
            }).sort('last_used', -1))
            
            for session in sessions:
                session['_id'] = str(session['_id'])
            
            return {
                'success': True,
                'data': sessions,
                'count': len(sessions)
            }
        except Exception as e:
            logger.error(f"Error obteniendo sesiones activas: {str(e)}")
            return {
                'success': False,
                'errors': [f'Error obteniendo sesiones: {str(e)}']
            }
    
    def invalidate_session(self, session_id=None, jti=None):
        """Invalidar una sesión específica"""
        try:
            query = {}
            if session_id:
                query['_id'] = ObjectId(session_id)
            elif jti:
                query['refresh_token_jti'] = jti
            else:
                return {'success': False, 'errors': ['Debe proporcionar session_id o jti']}
            
            result = self.collection.update_one(
                query,
                {'$set': {'active': False, 'invalidated_at': datetime.utcnow()}}
            )
            
            if result.modified_count > 0:
                return {
                    'success': True,
                    'message': 'Sesión invalidada correctamente'
                }
            else:
                return {
                    'success': False,
                    'errors': ['Sesión no encontrada']
                }
        except Exception as e:
            logger.error(f"Error invalidando sesión: {str(e)}")
            return {
                'success': False,
                'errors': [f'Error invalidando sesión: {str(e)}']
            }
    
    def invalidate_all_user_sessions(self, user_id, exclude_jti=None):
        """Invalidar todas las sesiones de un usuario (excepto opcionalmente una)"""
        try:
            query = {
                'user_id': user_id,
                'active': True
            }
            
            if exclude_jti:
                query['refresh_token_jti'] = {'$ne': exclude_jti}
            
            result = self.collection.update_many(
                query,
                {'$set': {'active': False, 'invalidated_at': datetime.utcnow()}}
            )
            
            return {
                'success': True,
                'message': f'{result.modified_count} sesiones invalidadas',
                'invalidated_count': result.modified_count
            }
        except Exception as e:
            logger.error(f"Error invalidando sesiones del usuario: {str(e)}")
            return {
                'success': False,
                'errors': [f'Error invalidando sesiones: {str(e)}']
            }
    
    def cleanup_expired_sessions(self):
        """Limpiar sesiones expiradas (para job de limpieza)"""
        try:
            # Eliminar sesiones expiradas hace más de 30 días
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            result = self.collection.delete_many({
                '$or': [
                    {'expires_at': {'$lt': datetime.utcnow()}},
                    {'created_at': {'$lt': cutoff_date}}
                ]
            })
            
            return {
                'success': True,
                'message': f'{result.deleted_count} sesiones expiradas eliminadas',
                'deleted_count': result.deleted_count
            }
        except Exception as e:
            logger.error(f"Error limpiando sesiones: {str(e)}")
            return {
                'success': False,
                'errors': [f'Error en limpieza: {str(e)}']
            }
    
    def get_session_stats(self):
        """Obtener estadísticas de sesiones"""
        try:
            pipeline = [
                {
                    '$group': {
                        '_id': None,
                        'total_sessions': {'$sum': 1},
                        'active_sessions': {
                            '$sum': {
                                '$cond': [
                                    {
                                        '$and': [
                                            {'$eq': ['$active', True]},
                                            {'$gt': ['$expires_at', datetime.utcnow()]}
                                        ]
                                    },
                                    1, 0
                                ]
                            }
                        },
                        'expired_sessions': {
                            '$sum': {
                                '$cond': [
                                    {'$lt': ['$expires_at', datetime.utcnow()]},
                                    1, 0
                                ]
                            }
                        }
                    }
                }
            ]
            
            stats = list(self.collection.aggregate(pipeline))
            
            if stats:
                result = stats[0]
                result.pop('_id', None)
                return {
                    'success': True,
                    'data': result
                }
            else:
                return {
                    'success': True,
                    'data': {
                        'total_sessions': 0,
                        'active_sessions': 0,
                        'expired_sessions': 0
                    }
                }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de sesiones: {str(e)}")
            return {
                'success': False,
                'errors': [f'Error obteniendo estadísticas: {str(e)}']
            }

    def get_active_session_duration_stats(self):
        """Promedio de duración de sesiones activas en minutos"""
        try:
            pipeline = [
                {
                    '$match': {
                        'active': True,
                        'expires_at': {'$gt': datetime.utcnow()}
                    }
                },
                {
                    '$project': {
                        'duration_ms': {'$subtract': ['$last_used', '$created_at']}
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'avg_duration_ms': {'$avg': '$duration_ms'},
                        'active_sessions': {'$sum': 1}
                    }
                }
            ]

            stats = list(self.collection.aggregate(pipeline))
            if not stats:
                return {
                    'success': True,
                    'data': {
                        'avg_session_duration': 0,
                        'active_sessions': 0
                    }
                }

            result = stats[0]
            avg_ms = result.get('avg_duration_ms') or 0
            avg_minutes = avg_ms / 60000
            return {
                'success': True,
                'data': {
                    'avg_session_duration': int(round(avg_minutes)),
                    'active_sessions': result.get('active_sessions', 0)
                }
            }
        except Exception as e:
            logger.error(f"Error obteniendo duración de sesiones: {str(e)}")
            return {
                'success': False,
                'errors': [f'Error obteniendo duración de sesiones: {str(e)}']
            }
