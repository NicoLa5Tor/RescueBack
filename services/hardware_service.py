from bson import ObjectId
from models.hardware import Hardware
from repositories.hardware_repository import HardwareRepository
from repositories.empresa_repository import EmpresaRepository
from services.hardware_type_service import HardwareTypeService
from utils.geocoding import procesar_direccion_para_hardware

class HardwareService:
    def __init__(self):
        self.hardware_repo = HardwareRepository()
        self.empresa_repo = EmpresaRepository()
        self.type_service = HardwareTypeService()


    def _get_empresa(self, empresa_nombre):
        """Obtiene la empresa a partir de su nombre."""
        return self.empresa_repo.find_by_nombre(empresa_nombre)
    
    def _procesar_direccion(self, direccion):
        """Procesa una dirección y devuelve URL, coordenadas y posible error."""
        if not direccion:
            return None, None, "La dirección es obligatoria"
        return procesar_direccion_para_hardware(direccion)

    def create_hardware(self, data):
        try:
            nombre = data.pop('nombre', None)
            tipo = data.pop('tipo', None)
            sede = data.pop('sede', None)
            direccion = data.pop('direccion', None)  # Nueva dirección
            nombre_empresa = data.pop('empresa_nombre', None)
            if not nombre_empresa:
                return {'success': False, 'errors': ['El nombre de la empresa es obligatorio']}
            empresa = self._get_empresa(nombre_empresa)
            if not empresa:
                return {'success': False, 'errors': ['Empresa no encontrada']}
            if not sede:
                return {'success': False, 'errors': ['La sede es obligatoria']}
            if sede not in (empresa.sedes or []):
                return {'success': False, 'errors': ['La sede no pertenece a la empresa']}
            if not nombre:
                return {'success': False, 'errors': ['El nombre del hardware es obligatorio']}
            if not direccion:
                return {'success': False, 'errors': ['La dirección es obligatoria']}
            if self.hardware_repo.find_by_nombre(nombre):
                return {'success': False, 'errors': ['Ya existe un hardware con ese nombre']}
            if tipo not in self.type_service.get_type_names():
                return {'success': False, 'errors': ['Tipo de hardware no soportado']}
            # Si los datos vienen con un campo 'datos', extraerlo; si no, usar data directamente
            datos_finales = data.get('datos', data) if 'datos' in data else data
            
            # Procesar dirección y geocodificar
            direccion_url, coordenadas, direccion_error = self._procesar_direccion(direccion)
            if direccion_error:
                return {'success': False, 'errors': [direccion_error]}
            
            # Crear instancia de hardware y generar topic automáticamente
            hardware = Hardware(nombre=nombre, tipo=tipo, empresa_id=empresa._id, sede=sede, datos=datos_finales)
            hardware.direccion = direccion
            hardware.direccion_url = direccion_url
            hardware.coordenadas = coordenadas  # Nuevo campo para coordenadas
            hardware.topic = hardware.generate_topic(nombre_empresa, sede, tipo, nombre)
            
            created = self.hardware_repo.create(hardware)
            result = created.to_json()
            result['empresa_nombre'] = nombre_empresa
            return {'success': True, 'data': result}
        except Exception as exc:
            return {'success': False, 'errors': [str(exc)]}

    def get_all_hardware(self, filters=None):
        try:
            if filters:
                hardware_list = self.hardware_repo.find_with_filters(filters)
            else:
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

    def get_hardware_including_inactive(self, hardware_id):
        """Obtiene hardware por ID incluyendo inactivos (para admins)"""
        try:
            hardware = self.hardware_repo.find_by_id_including_inactive(hardware_id)
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

    def get_all_hardware_including_inactive(self, filters=None):
        """Obtiene todos los hardware incluyendo los inactivos"""
        try:
            if filters:
                hardware_list = self.hardware_repo.find_with_filters_including_inactive(filters)
            else:
                hardware_list = self.hardware_repo.find_all_including_inactive()
            
            resultados = []
            for h in hardware_list:
                empresa = self.empresa_repo.find_by_id(h.empresa_id) if h.empresa_id else None
                j = h.to_json()
                j['empresa_nombre'] = empresa.nombre if empresa else None
                resultados.append(j)
            return {'success': True, 'data': resultados, 'count': len(resultados)}
        except Exception as exc:
            return {'success': False, 'errors': [str(exc)]}

    def get_hardware_by_empresa_including_inactive(self, empresa_id):
        """Obtiene todos los hardware de una empresa incluyendo los inactivos"""
        try:
            hardware_list = self.hardware_repo.find_by_empresa_including_inactive(empresa_id)
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
            existing = self.hardware_repo.find_by_id_including_inactive(hardware_id)
            if not existing:
                return {'success': False, 'errors': ['Hardware no encontrado']}
            nombre = data.pop('nombre', existing.nombre)
            tipo = data.pop('tipo', existing.tipo)
            sede = data.pop('sede', existing.sede)
            direccion = data.pop('direccion', existing.direccion)  # Nueva dirección
            nombre_empresa = data.pop('empresa_nombre', None)
            empresa = None
            empresa_id = existing.empresa_id
            # Validar nombres duplicados solo si el nombre cambió
            if nombre != existing.nombre:
                existing_hardware = self.hardware_repo.find_by_nombre_excluding_id(nombre, hardware_id)
                if existing_hardware:
                    return {'success': False, 'errors': ['Ya existe un hardware con ese nombre']}
            if nombre_empresa:
                empresa = self._get_empresa(nombre_empresa)
                if not empresa:
                    return {'success': False, 'errors': ['Empresa no encontrada']}
                empresa_id = empresa._id
            else:
                empresa = self.empresa_repo.find_by_id(existing.empresa_id) if existing.empresa_id else None
            if not sede:
                return {'success': False, 'errors': ['La sede es obligatoria']}
            if not direccion:
                return {'success': False, 'errors': ['La dirección es obligatoria']}
            if empresa and sede not in (empresa.sedes or []):
                return {'success': False, 'errors': ['La sede no pertenece a la empresa']}
            if tipo not in self.type_service.get_type_names():
                return {'success': False, 'errors': ['Tipo de hardware no soportado']}
            # Si los datos vienen con un campo 'datos', extraerlo; si no, usar data directamente
            datos_finales = data.get('datos', data) if 'datos' in data else data
            
            # Procesar dirección solo si cambió
            direccion_url = existing.direccion_url
            coordenadas = getattr(existing, 'coordenadas', None)
            
            if direccion != getattr(existing, 'direccion', None):
                print(f'🗺️ Dirección cambió, geocodificando nueva dirección: {direccion}')
                direccion_url, coordenadas, direccion_error = self._procesar_direccion(direccion)
                if direccion_error:
                    return {'success': False, 'errors': [direccion_error]}
            else:
                print(f'🔄 Dirección sin cambios, manteniendo URL existente')
            
            # Crear instancia actualizada y regenerar topic automáticamente
            updated = Hardware(nombre=nombre, tipo=tipo, empresa_id=empresa_id, sede=sede, datos=datos_finales, _id=existing._id, activa=existing.activa)
            updated.direccion = direccion
            updated.direccion_url = direccion_url
            updated.coordenadas = coordenadas
            updated.fecha_creacion = existing.fecha_creacion
            
            # Regenerar topic con los nuevos datos
            empresa_nombre_final = nombre_empresa if nombre_empresa else (empresa.nombre if empresa else None)
            if empresa_nombre_final:
                updated.topic = updated.generate_topic(empresa_nombre_final, sede, tipo, nombre)
            
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

    def toggle_hardware_status(self, hardware_id, activa):
        """Activar o desactivar hardware"""
        try:
            existing = self.hardware_repo.find_by_id_including_inactive(hardware_id)
            if not existing:
                return {'success': False, 'errors': ['Hardware no encontrado']}
            
            # Actualizar solo el campo activa
            existing.activa = activa
            existing.update_timestamp()
            
            updated = self.hardware_repo.update(hardware_id, existing)
            if updated:
                status_text = "activado" if activa else "desactivado"
                result = updated.to_json()
                empresa = self.empresa_repo.find_by_id(updated.empresa_id) if updated.empresa_id else None
                result['empresa_nombre'] = empresa.nombre if empresa else None
                return {
                    'success': True, 
                    'data': result,
                    'message': f'Hardware {status_text} exitosamente'
                }
            return {'success': False, 'errors': ['Error al actualizar el estado del hardware']}
        except Exception as exc:
            return {'success': False, 'errors': [str(exc)]}
    
    def get_hardware_direccion_url(self, hardware_id):
        """Obtiene solo la URL de dirección de un hardware específico"""
        try:
            hardware = self.hardware_repo.find_by_id_including_inactive(hardware_id)
            if not hardware:
                return {'success': False, 'errors': ['Hardware no encontrado']}
            
            # Retornar solo la información de dirección
            direccion_data = {
                'id': str(hardware._id),
                'nombre': hardware.nombre,
                'direccion': hardware.direccion,
                'direccion_url': hardware.direccion_url,
                'direccion_open_maps': getattr(hardware, 'direccion_open_maps', None)
            }
            
            return {'success': True, 'data': direccion_data}
        except Exception as exc:
            return {'success': False, 'errors': [str(exc)]}
