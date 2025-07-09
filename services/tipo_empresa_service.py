from models.tipo_empresa import TipoEmpresa
from repositories.tipo_empresa_repository import TipoEmpresaRepository
from bson import ObjectId

class TipoEmpresaService:
    def __init__(self):
        self.repository = TipoEmpresaRepository()
    
    def create_tipo_empresa(self, data, usuario_id):
        """Crea un nuevo tipo de empresa"""
        try:
            # Crear el objeto TipoEmpresa
            tipo_empresa = TipoEmpresa(
                nombre=data.get('nombre'),
                descripcion=data.get('descripcion', ''),
                caracteristicas=data.get('caracteristicas', []),
                creado_por=ObjectId(usuario_id) if usuario_id else None
            )
            
            # Crear en el repositorio
            result = self.repository.create(tipo_empresa)
            return result
            
        except Exception as e:
            return {"success": False, "errors": [f"Error al crear tipo de empresa: {str(e)}"]}
    
    def get_tipo_empresa_by_id(self, tipo_empresa_id):
        """Obtiene un tipo de empresa por su ID"""
        return self.repository.get_by_id(tipo_empresa_id)
    
    def get_all_tipos_empresa(self, skip=0, limit=100):
        """Obtiene todos los tipos de empresa"""
        return self.repository.get_all(skip, limit)
    
    def update_tipo_empresa(self, tipo_empresa_id, data):
        """Actualiza un tipo de empresa"""
        try:
            # Filtrar solo los campos permitidos para actualizar
            update_data = {}
            if 'nombre' in data:
                update_data['nombre'] = data['nombre']
            if 'descripcion' in data:
                update_data['descripcion'] = data['descripcion']
            if 'caracteristicas' in data:
                update_data['caracteristicas'] = data['caracteristicas']
            if 'activo' in data:
                update_data['activo'] = data['activo']
            
            return self.repository.update(tipo_empresa_id, update_data)
            
        except Exception as e:
            return {"success": False, "errors": [f"Error al actualizar tipo de empresa: {str(e)}"]}
    
    def delete_tipo_empresa(self, tipo_empresa_id):
        """Elimina lógicamente un tipo de empresa"""
        return self.repository.delete(tipo_empresa_id)
    
    def search_tipos_empresa(self, query, skip=0, limit=100):
        """Busca tipos de empresa por nombre o descripción"""
        if not query or len(query.strip()) == 0:
            return self.get_all_tipos_empresa(skip, limit)
        
        return self.repository.search(query.strip(), skip, limit)
    
    def get_tipo_empresa_by_nombre(self, nombre):
        """Obtiene un tipo de empresa por su nombre"""
        return self.repository.get_by_nombre(nombre)
    
    def validate_tipo_empresa_data(self, data, is_update=False):
        """Valida los datos de entrada para tipo de empresa"""
        errors = []
        
        # Validaciones para creación
        if not is_update:
            if not data.get('nombre'):
                errors.append("El nombre es obligatorio")
        
        # Validaciones comunes
        if 'nombre' in data:
            nombre = data['nombre'].strip() if data['nombre'] else ''
            if len(nombre) < 2:
                errors.append("El nombre debe tener al menos 2 caracteres")
            if len(nombre) > 50:
                errors.append("El nombre no puede exceder 50 caracteres")
        
        if 'descripcion' in data and data['descripcion']:
            descripcion = data['descripcion'].strip()
            if len(descripcion) > 200:
                errors.append("La descripción no puede exceder 200 caracteres")
        
        # Validaciones para características
        if 'caracteristicas' in data:
            caracteristicas = data['caracteristicas']
            if not isinstance(caracteristicas, list):
                errors.append("Las características deben ser una lista")
            else:
                for i, caracteristica in enumerate(caracteristicas):
                    if not isinstance(caracteristica, str):
                        errors.append(f"La característica {i+1} debe ser una cadena de texto")
                    elif len(caracteristica.strip()) == 0:
                        errors.append(f"La característica {i+1} no puede estar vacía")
                    elif len(caracteristica.strip()) > 100:
                        errors.append(f"La característica {i+1} no puede exceder 100 caracteres")
                
                if len(caracteristicas) > 20:
                    errors.append("No se pueden agregar más de 20 características")
        
        return errors
    
    def get_tipos_empresa_activos(self):
        """Obtiene solo los tipos de empresa activos (para selects/dropdowns)"""
        result = self.repository.get_all(skip=0, limit=1000)  # Obtener todos los activos
        if result["success"]:
            # Filtrar solo los campos necesarios para dropdowns
            tipos_simples = []
            for tipo in result["data"]:
                tipos_simples.append({
                    "_id": tipo["_id"],
                    "nombre": tipo["nombre"]
                })
            return {"success": True, "data": tipos_simples}
        return result
    
    def get_estadisticas_tipos_empresa(self):
        """Obtiene estadísticas de tipos de empresa"""
        return self.repository.get_estadisticas()
    
    def toggle_status_tipo_empresa(self, tipo_empresa_id):
        """Activa o desactiva un tipo de empresa"""
        return self.repository.toggle_status(tipo_empresa_id)
    
    def get_all_tipos_empresa_including_inactive(self, skip=0, limit=100):
        """Obtiene todos los tipos de empresa incluyendo inactivos (para administración)"""
        return self.repository.get_all_including_inactive(skip, limit)
    
    def get_promedio_empresas_por_tipo(self):
        """Obtiene el promedio de empresas por tipo de empresa"""
        return self.repository.get_promedio_empresas_por_tipo()
    
    def get_total_empresas_categorizadas(self):
        """Obtiene el total de empresas que tienen tipo asignado"""
        return self.repository.get_total_empresas_categorizadas()
