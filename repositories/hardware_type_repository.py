from bson import ObjectId
from datetime import datetime
from core.database import Database
from models.hardware_type import HardwareType

class HardwareTypeRepository:
    def __init__(self):
        self.collection = Database().get_database().hardware_types
        self._create_indexes()

    def _create_indexes(self):
        try:
            self.collection.create_index([('nombre', 1)], unique=True)
            self.collection.create_index([('activa', 1)])
        except Exception as exc:
            # print(f'Error creando indices hardware_types: {exc}')
            pass

    def create(self, hw_type: HardwareType):
        try:
            data = hw_type.to_dict()
            result = self.collection.insert_one(data)
            hw_type._id = result.inserted_id
            return hw_type
        except Exception as exc:
            raise Exception(f'Error creando tipo hardware: {str(exc)}')

    def find_by_id(self, type_id):
        try:
            if isinstance(type_id, str):
                type_id = ObjectId(type_id)
            data = self.collection.find_one({'_id': type_id, 'activa': True})
            return HardwareType.from_dict(data) if data else None
        except Exception as exc:
            raise Exception(f'Error buscando tipo por ID: {str(exc)}')

    def find_by_nombre(self, nombre):
        try:
            data = self.collection.find_one({'nombre': nombre, 'activa': True})
            return HardwareType.from_dict(data) if data else None
        except Exception as exc:
            raise Exception(f'Error buscando tipo por nombre: {str(exc)}')

    def find_by_nombre_excluding_id(self, nombre, exclude_id):
        """Busca tipo de hardware por nombre excluyendo un ID específico"""
        try:
            if isinstance(exclude_id, str):
                exclude_id = ObjectId(exclude_id)
            data = self.collection.find_one({
                'nombre': nombre, 
                'activa': True,
                '_id': {'$ne': exclude_id}
            })
            return HardwareType.from_dict(data) if data else None
        except Exception as exc:
            raise Exception(f'Error buscando tipo por nombre (excluyendo ID): {str(exc)}')

    def find_all(self):
        try:
            cursor = self.collection.find({'activa': True}).sort('fecha_creacion', -1)
            return [HardwareType.from_dict(d) for d in cursor]
        except Exception as exc:
            raise Exception(f'Error obteniendo tipos: {str(exc)}')

    def update(self, type_id, hw_type: HardwareType):
        try:
            if isinstance(type_id, str):
                type_id = ObjectId(type_id)
            hw_type.update_timestamp()
            data = hw_type.to_dict()
            data.pop('_id', None)
            result = self.collection.update_one({'_id': type_id, 'activa': True}, {'$set': data})
            if result.matched_count > 0:
                return self.find_by_id(type_id)
            return None
        except Exception as exc:
            raise Exception(f'Error actualizando tipo: {str(exc)}')

    def soft_delete(self, type_id):
        try:
            if isinstance(type_id, str):
                type_id = ObjectId(type_id)
            result = self.collection.update_one({'_id': type_id, 'activa': True}, {'$set': {'activa': False, 'fecha_actualizacion': datetime.utcnow()}})
            return result.modified_count > 0
        except Exception as exc:
            raise Exception(f'Error eliminando tipo: {str(exc)}')
