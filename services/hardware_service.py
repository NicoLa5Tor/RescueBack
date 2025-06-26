import json
from bson import ObjectId
from models.hardware import Hardware
from repositories.hardware_repository import HardwareRepository
from repositories.empresa_repository import EmpresaRepository
from pathlib import Path

class HardwareService:
    def __init__(self):
        self.hardware_repo = HardwareRepository()
        self.empresa_repo = EmpresaRepository()
        self.hardware_types = self._load_types()

    def _load_types(self):
        path = Path(__file__).resolve().parent.parent / 'models' / 'hardwaremodel.json'
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('hardware_types', [])
        except Exception:
            return []

    def _get_empresa_id(self, empresa_nombre):
        empresa = self.empresa_repo.find_by_nombre(empresa_nombre)
        if not empresa:
            return None
        return empresa._id

    def create_hardware(self, data):
        try:
            nombre = data.pop('nombre', None)
            tipo = data.pop('tipo', None)
            sede = data.pop('sede', None)
            nombre_empresa = data.pop('empresa_nombre', None)
            if not nombre_empresa:
                return {'success': False, 'errors': ['El nombre de la empresa es obligatorio']}
            empresa_id = self._get_empresa_id(nombre_empresa)
            if not empresa_id:
                return {'success': False, 'errors': ['Empresa no encontrada']}
            if not nombre:
                return {'success': False, 'errors': ['El nombre del hardware es obligatorio']}
            if self.hardware_repo.find_by_nombre(nombre):
                return {'success': False, 'errors': ['Ya existe un hardware con ese nombre']}
            if tipo not in self.hardware_types:
                return {'success': False, 'errors': ['Tipo de hardware no soportado']}
            hardware = Hardware(nombre=nombre, tipo=tipo, empresa_id=empresa_id, sede=sede, datos=data)
            created = self.hardware_repo.create(hardware)
            result = created.to_json()
            result['empresa_nombre'] = nombre_empresa
            return {'success': True, 'data': result}
        except Exception as exc:
            return {'success': False, 'errors': [str(exc)]}

    def get_all_hardware(self):
        try:
            hardware_list = self.hardware_repo.find_all()
            resultados = []
            for h in hardware_list:
                empresa = self.empresa_repo.find_by_id(h.empresa_id) if h.empresa_id else None
                j = h.to_json()
                j['empresa_nombre'] = empresa.nombre if empresa else None
                resultados.append(j)
            return {'success': True, 'data': resultados, 'count': len(resultados)}
        except Exception as exc:
            return {'success': False, 'errors': [str(exc)]}

    def get_hardware(self, hardware_id):
        try:
            hardware = self.hardware_repo.find_by_id(hardware_id)
            if not hardware:
                return {'success': False, 'errors': ['Hardware no encontrado']}
            empresa = self.empresa_repo.find_by_id(hardware.empresa_id) if hardware.empresa_id else None
            result = hardware.to_json()
            result['empresa_nombre'] = empresa.nombre if empresa else None
            return {'success': True, 'data': result}
        except Exception as exc:
            return {'success': False, 'errors': [str(exc)]}

    def get_hardware_by_empresa(self, empresa_id):
        try:
            hardware_list = self.hardware_repo.find_by_empresa(empresa_id)
            empresa = self.empresa_repo.find_by_id(empresa_id)
            nombre = empresa.nombre if empresa else None
            resultados = []
            for h in hardware_list:
                j = h.to_json()
                j['empresa_nombre'] = nombre
                resultados.append(j)
            return {'success': True, 'data': resultados, 'count': len(resultados)}
        except Exception as exc:
            return {'success': False, 'errors': [str(exc)]}

    def update_hardware(self, hardware_id, data):
        try:
            existing = self.hardware_repo.find_by_id(hardware_id)
            if not existing:
                return {'success': False, 'errors': ['Hardware no encontrado']}
            nombre = data.pop('nombre', existing.nombre)
            tipo = data.pop('tipo', existing.tipo)
            sede = data.pop('sede', existing.sede)
            nombre_empresa = data.pop('empresa_nombre', None)
            empresa_id = existing.empresa_id
            if nombre != existing.nombre and self.hardware_repo.find_by_nombre(nombre):
                return {'success': False, 'errors': ['Ya existe un hardware con ese nombre']}
            if nombre_empresa:
                empresa_id = self._get_empresa_id(nombre_empresa)
                if not empresa_id:
                    return {'success': False, 'errors': ['Empresa no encontrada']}
            if tipo not in self.hardware_types:
                return {'success': False, 'errors': ['Tipo de hardware no soportado']}
            updated = Hardware(nombre=nombre, tipo=tipo, empresa_id=empresa_id, sede=sede, datos=data, _id=existing._id, activa=existing.activa)
            updated.fecha_creacion = existing.fecha_creacion
            result = self.hardware_repo.update(hardware_id, updated)
            if result:
                res = result.to_json()
                empresa = self.empresa_repo.find_by_id(result.empresa_id) if result.empresa_id else None
                res['empresa_nombre'] = empresa.nombre if empresa else None
                return {'success': True, 'data': res}
            else:
                return {'success': False, 'errors': ['Error actualizando hardware']}
        except Exception as exc:
            return {'success': False, 'errors': [str(exc)]}

    def delete_hardware(self, hardware_id):
        try:
            deleted = self.hardware_repo.soft_delete(hardware_id)
            if deleted:
                return {'success': True, 'message': 'Hardware eliminado correctamente'}
            return {'success': False, 'errors': ['Error eliminando hardware']}
        except Exception as exc:
            return {'success': False, 'errors': [str(exc)]}
