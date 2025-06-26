from bson import ObjectId
from datetime import datetime
from database import Database
from models.hardware import Hardware

class HardwareRepository:
    def __init__(self):
        self.collection = Database().get_database().hardware
        self._create_indexes()

    def _create_indexes(self):
        try:
            self.collection.create_index([('nombre', 1)], unique=True)
            self.collection.create_index([('empresa_id', 1)])
            self.collection.create_index([('activa', 1)])
        except Exception as exc:
            print(f'Error creando indices de hardware: {exc}')

    def create(self, hardware: Hardware):
        try:
            hw_dict = hardware.to_dict()
            result = self.collection.insert_one(hw_dict)
            hardware._id = result.inserted_id
            return hardware
        except Exception as exc:
            raise Exception(f'Error creando hardware: {str(exc)}')

    def find_by_id(self, hardware_id):
        try:
            if isinstance(hardware_id, str):
                hardware_id = ObjectId(hardware_id)
            data = self.collection.find_one({'_id': hardware_id, 'activa': True})
            return Hardware.from_dict(data) if data else None
        except Exception as exc:
            raise Exception(f'Error buscando hardware por ID: {str(exc)}')

    def find_by_nombre(self, nombre):
        try:
            data = self.collection.find_one({'nombre': nombre, 'activa': True})
            return Hardware.from_dict(data) if data else None
        except Exception as exc:
            raise Exception(f'Error buscando hardware por nombre: {str(exc)}')

    def find_all(self):
        try:
            cursor = self.collection.find({'activa': True}).sort('fecha_creacion', -1)
            return [Hardware.from_dict(d) for d in cursor]
        except Exception as exc:
            raise Exception(f'Error obteniendo hardware: {str(exc)}')

    def find_by_empresa(self, empresa_id):
        try:
            if isinstance(empresa_id, str):
                empresa_id = ObjectId(empresa_id)
            cursor = self.collection.find({'empresa_id': empresa_id, 'activa': True}).sort('fecha_creacion', -1)
            return [Hardware.from_dict(d) for d in cursor]
        except Exception as exc:
            raise Exception(f'Error obteniendo hardware por empresa: {str(exc)}')

    def update(self, hardware_id, hardware: Hardware):
        try:
            if isinstance(hardware_id, str):
                hardware_id = ObjectId(hardware_id)
            hardware.update_timestamp()
            hw_dict = hardware.to_dict()
            hw_dict.pop('_id', None)
            result = self.collection.update_one({'_id': hardware_id, 'activa': True}, {'$set': hw_dict})
            if result.matched_count > 0:
                return self.find_by_id(hardware_id)
            return None
        except Exception as exc:
            raise Exception(f'Error actualizando hardware: {str(exc)}')

    def soft_delete(self, hardware_id):
        try:
            if isinstance(hardware_id, str):
                hardware_id = ObjectId(hardware_id)
            result = self.collection.update_one({'_id': hardware_id, 'activa': True}, {'$set': {'activa': False, 'fecha_actualizacion': datetime.utcnow()}})
            return result.modified_count > 0
        except Exception as exc:
            raise Exception(f'Error eliminando hardware: {str(exc)}')
