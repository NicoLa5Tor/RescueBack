from database import Database
from models.tipo_alarma import TipoAlarma
from bson import ObjectId
from datetime import datetime

class TipoAlarmaRepository:
    """Repositorio para operaciones de tipos de alarma"""
    
    def __init__(self):
        self.db = Database().get_database()
        self.collection = self.db.tipos_alarma
    
    def create_tipo_alarma(self, tipo_alarma):
        """Crea un nuevo tipo de alarma"""
        try:
            tipo_alarma.normalize_data()
            result = self.collection.insert_one(tipo_alarma.to_dict())
            tipo_alarma._id = result.inserted_id
            return tipo_alarma
        except Exception as e:
            print(f"Error creando tipo de alarma: {e}")
            raise e
    
    def get_tipo_alarma_by_id(self, tipo_alarma_id):
        """Obtiene un tipo de alarma por su ID"""
        try:
            tipo_alarma_data = self.collection.find_one({'_id': ObjectId(tipo_alarma_id)})
            if tipo_alarma_data:
                return TipoAlarma.from_dict(tipo_alarma_data)
            return None
        except Exception as e:
            print(f"Error obteniendo tipo de alarma por ID: {e}")
            return None
    
    def get_all_tipos_alarma(self, page=1, limit=50):
        """Obtiene todos los tipos de alarma con paginación"""
        try:
            skip = (page - 1) * limit
            tipos_alarma_data = self.collection.find().sort('fecha_creacion', -1).skip(skip).limit(limit)
            tipos_alarma = [TipoAlarma.from_dict(tipo_data) for tipo_data in tipos_alarma_data]
            total = self.collection.count_documents({})
            return tipos_alarma, total
        except Exception as e:
            print(f"Error obteniendo tipos de alarma: {e}")
            return [], 0
    
    def get_tipos_alarma_by_empresa(self, empresa_id, page=1, limit=50):
        """Obtiene tipos de alarma por empresa"""
        try:
            skip = (page - 1) * limit
            query = {'empresa_id': ObjectId(empresa_id)}
            tipos_alarma_data = self.collection.find(query).sort('fecha_creacion', -1).skip(skip).limit(limit)
            tipos_alarma = [TipoAlarma.from_dict(tipo_data) for tipo_data in tipos_alarma_data]
            total = self.collection.count_documents(query)
            return tipos_alarma, total
        except Exception as e:
            print(f"Error obteniendo tipos de alarma por empresa: {e}")
            return [], 0
    
    def get_tipos_alarma_by_tipo_alerta(self, tipo_alerta, page=1, limit=50):
        """Obtiene tipos de alarma por tipo de alerta (color)"""
        try:
            skip = (page - 1) * limit
            query = {'tipo_alerta': tipo_alerta}
            tipos_alarma_data = self.collection.find(query).sort('fecha_creacion', -1).skip(skip).limit(limit)
            tipos_alarma = [TipoAlarma.from_dict(tipo_data) for tipo_data in tipos_alarma_data]
            total = self.collection.count_documents(query)
            return tipos_alarma, total
        except Exception as e:
            print(f"Error obteniendo tipos de alarma por tipo de alerta: {e}")
            return [], 0
    
    def find_by_tipo_alerta(self, tipo_alerta):
        """Busca el primer tipo de alarma que coincida con el tipo de alerta"""
        try:
            query = {'tipo_alerta': tipo_alerta, 'activo': True}
            tipo_alarma_data = self.collection.find_one(query)
            if tipo_alarma_data:
                return TipoAlarma.from_dict(tipo_alarma_data)
            return None
        except Exception as e:
            print(f"Error buscando tipo de alarma por tipo de alerta: {e}")
            return None
    
    def get_active_tipos_alarma(self, page=1, limit=50):
        """Obtiene tipos de alarma activos"""
        try:
            skip = (page - 1) * limit
            query = {'activo': True}
            tipos_alarma_data = self.collection.find(query).sort('fecha_creacion', -1).skip(skip).limit(limit)
            tipos_alarma = [TipoAlarma.from_dict(tipo_data) for tipo_data in tipos_alarma_data]
            total = self.collection.count_documents(query)
            return tipos_alarma, total
        except Exception as e:
            print(f"Error obteniendo tipos de alarma activos: {e}")
            return [], 0
    
    def get_tipos_alarma_by_empresa_and_tipo(self, empresa_id, tipo_alerta):
        """Obtiene tipos de alarma por empresa y tipo de alerta"""
        try:
            query = {'empresa_id': ObjectId(empresa_id), 'tipo_alerta': tipo_alerta, 'activo': True}
            tipos_alarma_data = self.collection.find(query)
            tipos_alarma = [TipoAlarma.from_dict(tipo_data) for tipo_data in tipos_alarma_data]
            return tipos_alarma
        except Exception as e:
            print(f"Error obteniendo tipos de alarma por empresa y tipo: {e}")
            return []
    
    def update_tipo_alarma(self, tipo_alarma_id, tipo_alarma):
        """Actualiza un tipo de alarma"""
        try:
            tipo_alarma.normalize_data()
            tipo_alarma.update_timestamp()
            update_data = tipo_alarma.to_dict()
            del update_data['_id']  # No actualizar el ID
            
            result = self.collection.update_one(
                {'_id': ObjectId(tipo_alarma_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error actualizando tipo de alarma: {e}")
            return False
    
    def toggle_tipo_alarma_status(self, tipo_alarma_id):
        """Alterna el estado activo de un tipo de alarma"""
        try:
            tipo_alarma = self.get_tipo_alarma_by_id(tipo_alarma_id)
            if not tipo_alarma:
                return False
            
            new_status = not tipo_alarma.activo
            result = self.collection.update_one(
                {'_id': ObjectId(tipo_alarma_id)},
                {
                    '$set': {
                        'activo': new_status,
                        'fecha_actualizacion': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error cambiando estado de tipo de alarma: {e}")
            return False
    
    def delete_tipo_alarma(self, tipo_alarma_id):
        """Elimina un tipo de alarma"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(tipo_alarma_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error eliminando tipo de alarma: {e}")
            return False
    
    def get_tipos_alarma_stats(self):
        """Obtiene estadísticas de tipos de alarma"""
        try:
            total = self.collection.count_documents({})
            active = self.collection.count_documents({'activo': True})
            
            # Contar por tipo de alerta
            tipos_stats = {}
            for tipo in TipoAlarma.TIPOS_ALERTA.values():
                count = self.collection.count_documents({'tipo_alerta': tipo})
                tipos_stats[tipo] = count
            
            return {
                'total': total,
                'active': active,
                'inactive': total - active,
                'por_tipo': tipos_stats
            }
        except Exception as e:
            print(f"Error obteniendo estadísticas de tipos de alarma: {e}")
            return {
                'total': 0,
                'active': 0,
                'inactive': 0,
                'por_tipo': {}
            }
    
    def verify_empresa_exists(self, empresa_id):
        """Verifica si existe una empresa"""
        try:
            empresa = self.db.empresas.find_one({'_id': ObjectId(empresa_id)})
            return empresa is not None
        except Exception as e:
            print(f"Error verificando empresa: {e}")
            return False
    
    def check_duplicate_name(self, nombre, empresa_id, exclude_id=None):
        """Verifica si ya existe un tipo de alarma con el mismo nombre para la empresa"""
        try:
            query = {'nombre': nombre, 'empresa_id': ObjectId(empresa_id)}
            if exclude_id:
                query['_id'] = {'$ne': ObjectId(exclude_id)}
            
            existing = self.collection.find_one(query)
            return existing is not None
        except Exception as e:
            print(f"Error verificando duplicado: {e}")
            return False
    
    def search_tipos_alarma(self, search_term, page=1, limit=50):
        """Busca tipos de alarma por nombre o descripción"""
        try:
            skip = (page - 1) * limit
            query = {
                '$or': [
                    {'nombre': {'$regex': search_term, '$options': 'i'}},
                    {'descripcion': {'$regex': search_term, '$options': 'i'}}
                ]
            }
            tipos_alarma_data = self.collection.find(query).sort('fecha_creacion', -1).skip(skip).limit(limit)
            tipos_alarma = [TipoAlarma.from_dict(tipo_data) for tipo_data in tipos_alarma_data]
            total = self.collection.count_documents(query)
            return tipos_alarma, total
        except Exception as e:
            print(f"Error buscando tipos de alarma: {e}")
            return [], 0
    
    def bulk_create_tipos_alarma(self, tipos_alarma_list):
        """Crea múltiples tipos de alarma en una sola operación"""
        try:
            documents = []
            for tipo_alarma in tipos_alarma_list:
                tipo_alarma.normalize_data()
                documents.append(tipo_alarma.to_dict())
            
            result = self.collection.insert_many(documents)
            return len(result.inserted_ids)
        except Exception as e:
            print(f"Error creando tipos de alarma en lote: {e}")
            return 0
    
    def update_imagen_tipo_alarma(self, tipo_alarma_id, imagen_base64):
        """Actualiza solo la imagen de un tipo de alarma"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(tipo_alarma_id)},
                {
                    '$set': {
                        'imagen_base64': imagen_base64,
                        'fecha_actualizacion': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error actualizando imagen: {e}")
            return False
    
    def add_recomendacion_to_tipo_alarma(self, tipo_alarma_id, recomendacion):
        """Agrega una recomendación a un tipo de alarma"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(tipo_alarma_id)},
                {
                    '$push': {'recomendaciones': recomendacion.strip()},
                    '$set': {'fecha_actualizacion': datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error agregando recomendación: {e}")
            return False
    
    def remove_recomendacion_from_tipo_alarma(self, tipo_alarma_id, recomendacion):
        """Elimina una recomendación de un tipo de alarma"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(tipo_alarma_id)},
                {
                    '$pull': {'recomendaciones': recomendacion},
                    '$set': {'fecha_actualizacion': datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error eliminando recomendación: {e}")
            return False
    
    def add_implemento_to_tipo_alarma(self, tipo_alarma_id, implemento):
        """Agrega un implemento a un tipo de alarma"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(tipo_alarma_id)},
                {
                    '$push': {'implementos_necesarios': implemento.strip()},
                    '$set': {'fecha_actualizacion': datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error agregando implemento: {e}")
            return False
    
    def remove_implemento_from_tipo_alarma(self, tipo_alarma_id, implemento):
        """Elimina un implemento de un tipo de alarma"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(tipo_alarma_id)},
                {
                    '$pull': {'implementos_necesarios': implemento},
                    '$set': {'fecha_actualizacion': datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error eliminando implemento: {e}")
            return False
