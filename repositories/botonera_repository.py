from bson import ObjectId
from datetime import datetime
from database import Database
from models.botonera import Botonera

class BotoneraRepository:
    def __init__(self):
        self.collection = Database().get_database().botoneras
        self._create_indexes()

    def _create_indexes(self):
        try:
            self.collection.create_index([('empresa_id', 1)])
            self.collection.create_index([('activa', 1)])
        except Exception as exc:
            print(f'Error creando indices de botoneras: {exc}')

    def create(self, botonera: Botonera):
        try:
            botonera_dict = botonera.to_dict()
            result = self.collection.insert_one(botonera_dict)
            botonera._id = result.inserted_id
            return botonera
        except Exception as exc:
            raise Exception(f'Error creando botonera: {str(exc)}')

    def find_by_id(self, botonera_id):
        try:
            if isinstance(botonera_id, str):
                botonera_id = ObjectId(botonera_id)
            data = self.collection.find_one({'_id': botonera_id, 'activa': True})
            return Botonera.from_dict(data) if data else None
        except Exception as exc:
            raise Exception(f'Error buscando botonera por ID: {str(exc)}')

    def find_all(self):
        try:
            cursor = self.collection.find({'activa': True}).sort('fecha_creacion', -1)
            return [Botonera.from_dict(d) for d in cursor]
        except Exception as exc:
            raise Exception(f'Error obteniendo botoneras: {str(exc)}')

    def find_by_empresa(self, empresa_id):
        try:
            if isinstance(empresa_id, str):
                empresa_id = ObjectId(empresa_id)
            cursor = self.collection.find({'empresa_id': empresa_id, 'activa': True}).sort('fecha_creacion', -1)
            return [Botonera.from_dict(d) for d in cursor]
        except Exception as exc:
            raise Exception(f'Error obteniendo botoneras por empresa: {str(exc)}')

    def update(self, botonera_id, botonera: Botonera):
        try:
            if isinstance(botonera_id, str):
                botonera_id = ObjectId(botonera_id)
            botonera.update_timestamp()
            botonera_dict = botonera.to_dict()
            botonera_dict.pop('_id', None)
            result = self.collection.update_one({'_id': botonera_id, 'activa': True}, {'$set': botonera_dict})
            if result.matched_count > 0:
                return self.find_by_id(botonera_id)
            return None
        except Exception as exc:
            raise Exception(f'Error actualizando botonera: {str(exc)}')

    def soft_delete(self, botonera_id):
        try:
            if isinstance(botonera_id, str):
                botonera_id = ObjectId(botonera_id)
            result = self.collection.update_one({'_id': botonera_id, 'activa': True}, {'$set': {'activa': False, 'fecha_actualizacion': datetime.utcnow()}})
            return result.modified_count > 0
        except Exception as exc:
            raise Exception(f'Error eliminando botonera: {str(exc)}')
