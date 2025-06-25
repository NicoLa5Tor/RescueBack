from bson import ObjectId
from models.botonera import Botonera
from repositories.botonera_repository import BotoneraRepository
from repositories.empresa_repository import EmpresaRepository

class BotoneraService:
    def __init__(self):
        self.botonera_repo = BotoneraRepository()
        self.empresa_repo = EmpresaRepository()

    def _get_empresa_id(self, empresa_nombre):
        empresa = self.empresa_repo.find_by_nombre(empresa_nombre)
        if not empresa:
            return None
        return empresa._id

    def create_botonera(self, data):
        try:
            nombre_empresa = data.pop('empresa_nombre', None)
            if not nombre_empresa:
                return {'success': False, 'errors': ['El nombre de la empresa es obligatorio']}
            empresa_id = self._get_empresa_id(nombre_empresa)
            if not empresa_id:
                return {'success': False, 'errors': ['Empresa no encontrada']}
            botonera = Botonera(empresa_id=empresa_id, datos=data)
            created = self.botonera_repo.create(botonera)
            result = created.to_json()
            result['empresa_nombre'] = nombre_empresa
            return {'success': True, 'data': result}
        except Exception as exc:
            return {'success': False, 'errors': [str(exc)]}

    def get_all_botoneras(self):
        try:
            botoneras = self.botonera_repo.find_all()
            resultados = []
            for b in botoneras:
                empresa = self.empresa_repo.find_by_id(b.empresa_id) if b.empresa_id else None
                j = b.to_json()
                j['empresa_nombre'] = empresa.nombre if empresa else None
                resultados.append(j)
            return {'success': True, 'data': resultados, 'count': len(resultados)}
        except Exception as exc:
            return {'success': False, 'errors': [str(exc)]}

    def get_botonera(self, botonera_id):
        try:
            botonera = self.botonera_repo.find_by_id(botonera_id)
            if not botonera:
                return {'success': False, 'errors': ['Botonera no encontrada']}
            empresa = self.empresa_repo.find_by_id(botonera.empresa_id) if botonera.empresa_id else None
            result = botonera.to_json()
            result['empresa_nombre'] = empresa.nombre if empresa else None
            return {'success': True, 'data': result}
        except Exception as exc:
            return {'success': False, 'errors': [str(exc)]}

    def get_botoneras_by_empresa(self, empresa_id):
        try:
            botoneras = self.botonera_repo.find_by_empresa(empresa_id)
            empresa = self.empresa_repo.find_by_id(empresa_id)
            nombre = empresa.nombre if empresa else None
            resultados = []
            for b in botoneras:
                j = b.to_json()
                j['empresa_nombre'] = nombre
                resultados.append(j)
            return {'success': True, 'data': resultados, 'count': len(resultados)}
        except Exception as exc:
            return {'success': False, 'errors': [str(exc)]}

    def update_botonera(self, botonera_id, data):
        try:
            existing = self.botonera_repo.find_by_id(botonera_id)
            if not existing:
                return {'success': False, 'errors': ['Botonera no encontrada']}
            nombre_empresa = data.pop('empresa_nombre', None)
            empresa_id = existing.empresa_id
            if nombre_empresa:
                empresa_id = self._get_empresa_id(nombre_empresa)
                if not empresa_id:
                    return {'success': False, 'errors': ['Empresa no encontrada']}
            updated = Botonera(empresa_id=empresa_id, datos=data, _id=existing._id, activa=existing.activa)
            updated.fecha_creacion = existing.fecha_creacion
            result = self.botonera_repo.update(botonera_id, updated)
            if result:
                res = result.to_json()
                empresa = self.empresa_repo.find_by_id(result.empresa_id) if result.empresa_id else None
                res['empresa_nombre'] = empresa.nombre if empresa else None
                return {'success': True, 'data': res}
            else:
                return {'success': False, 'errors': ['Error actualizando botonera']}
        except Exception as exc:
            return {'success': False, 'errors': [str(exc)]}

    def delete_botonera(self, botonera_id):
        try:
            deleted = self.botonera_repo.soft_delete(botonera_id)
            if deleted:
                return {'success': True, 'message': 'Botonera eliminada correctamente'}
            return {'success': False, 'errors': ['Error eliminando botonera']}
        except Exception as exc:
            return {'success': False, 'errors': [str(exc)]}
