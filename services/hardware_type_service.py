from models.hardware_type import HardwareType
from repositories.hardware_type_repository import HardwareTypeRepository

class HardwareTypeService:
    def __init__(self):
        self.repo = HardwareTypeRepository()
        self._ensure_defaults()

    def _ensure_defaults(self):
        defaults = ['botonera', 'semaforo']
        existing = [t.nombre for t in self.repo.find_all()]
        for name in defaults:
            if name not in existing:
                hw_type = HardwareType(nombre=name)
                try:
                    self.repo.create(hw_type)
                except Exception:
                    pass

    def get_type_names(self):
        return [t.nombre for t in self.repo.find_all()]

    def create_type(self, data):
        nombre = data.get('nombre')
        descripcion = data.get('descripcion')
        if not nombre:
            return {'success': False, 'errors': ['El nombre es obligatorio']}
        if self.repo.find_by_nombre(nombre):
            return {'success': False, 'errors': ['El tipo ya existe']}
        hw_type = HardwareType(nombre=nombre, descripcion=descripcion)
        try:
            created = self.repo.create(hw_type)
            return {'success': True, 'data': created.to_json()}
        except Exception as exc:
            return {'success': False, 'errors': [str(exc)]}

    def get_all_types(self):
        try:
            tipos = [t.to_json() for t in self.repo.find_all()]
            return {'success': True, 'data': tipos, 'count': len(tipos)}
        except Exception as exc:
            return {'success': False, 'errors': [str(exc)]}

    def get_type(self, type_id):
        try:
            t = self.repo.find_by_id(type_id)
            if not t:
                return {'success': False, 'errors': ['Tipo no encontrado']}
            return {'success': True, 'data': t.to_json()}
        except Exception as exc:
            return {'success': False, 'errors': [str(exc)]}

    def update_type(self, type_id, data):
        try:
            existing = self.repo.find_by_id(type_id)
            if not existing:
                return {'success': False, 'errors': ['Tipo no encontrado']}
            nombre = data.get('nombre', existing.nombre)
            descripcion = data.get('descripcion', existing.descripcion)
            if nombre != existing.nombre and self.repo.find_by_nombre(nombre):
                return {'success': False, 'errors': ['El tipo ya existe']}
            updated = HardwareType(nombre=nombre, descripcion=descripcion, _id=existing._id, activa=existing.activa)
            updated.fecha_creacion = existing.fecha_creacion
            result = self.repo.update(type_id, updated)
            if result:
                return {'success': True, 'data': result.to_json()}
            else:
                return {'success': False, 'errors': ['Error actualizando tipo']}
        except Exception as exc:
            return {'success': False, 'errors': [str(exc)]}

    def delete_type(self, type_id):
        try:
            deleted = self.repo.soft_delete(type_id)
            if deleted:
                return {'success': True, 'message': 'Tipo eliminado correctamente'}
            return {'success': False, 'errors': ['Error eliminando tipo']}
        except Exception as exc:
            return {'success': False, 'errors': [str(exc)]}
