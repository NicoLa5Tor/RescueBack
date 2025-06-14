from bson import ObjectId
import bcrypt
from models.empresa import Empresa
from repositories.empresa_repository import EmpresaRepository

class EmpresaService:
    def __init__(self):
        self.empresa_repository = EmpresaRepository()
    
    def create_empresa(self, empresa_data, super_admin_id):
        """Crea una nueva empresa con validaciones"""
        try:
            # Validar que el super_admin_id sea válido
            if not super_admin_id:
                return {
                    'success': False,
                    'errors': ['El ID del super admin es obligatorio']
                }
            
            # Convertir super_admin_id a ObjectId si es string
            if isinstance(super_admin_id, str):
                try:
                    super_admin_id = ObjectId(super_admin_id)
                except Exception:
                    return {
                        'success': False,
                        'errors': ['El ID del super admin no es válido']
                    }
            
            password = empresa_data.get('password')
            email = empresa_data.get('email')

            # Crear objeto Empresa
            empresa = Empresa(
                nombre=empresa_data.get('nombre'),
                descripcion=empresa_data.get('descripcion'),
                ubicacion=empresa_data.get('ubicacion'),
                email=email,
                password_hash=None,
                creado_por=super_admin_id
            )

            if not password:
                return {
                    'success': False,
                    'errors': ['La contraseña es obligatoria']
                }
            # Hash password
            empresa.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Validar datos
            validation_errors = empresa.validate()
            if validation_errors:
                return {
                    'success': False,
                    'errors': validation_errors
                }
            
            # Verificar si el nombre ya existe
            existing_empresa = self.empresa_repository.find_by_nombre(empresa.nombre)
            if existing_empresa:
                return {
                    'success': False,
                    'errors': ['Ya existe una empresa con ese nombre']
                }

            # Verificar si el email ya existe
            if email:
                existing_email = self.empresa_repository.find_by_email(email)
                if existing_email:
                    return {
                        'success': False,
                        'errors': ['Ya existe una empresa con ese email']
                    }
            
            # Crear empresa
            created_empresa = self.empresa_repository.create(empresa)
            return {
                'success': True,
                'data': created_empresa.to_json(),
                'message': 'Empresa creada exitosamente'
            }
            
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            }
    
    def get_empresa_by_id(self, empresa_id):
        """Obtiene una empresa por ID"""
        try:
            empresa = self.empresa_repository.find_by_id(empresa_id)
            if empresa:
                return {
                    'success': True,
                    'data': empresa.to_json()
                }
            else:
                return {
                    'success': False,
                    'errors': ['Empresa no encontrada']
                }
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            }
    
    def get_all_empresas(self, include_inactive=False):
        """Obtiene todas las empresas"""
        try:
            empresas = self.empresa_repository.find_all(include_inactive)
            empresas_json = [empresa.to_json() for empresa in empresas]
            return {
                'success': True,
                'data': empresas_json,
                'count': len(empresas_json)
            }
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            }
    
    def get_empresas_by_creador(self, super_admin_id):
        """Obtiene empresas creadas por un super admin específico"""
        try:
            empresas = self.empresa_repository.find_by_creador(super_admin_id)
            empresas_json = [empresa.to_json() for empresa in empresas]
            return {
                'success': True,
                'data': empresas_json,
                'count': len(empresas_json)
            }
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            }
    
    def update_empresa(self, empresa_id, empresa_data, super_admin_id=None):
        """Actualiza una empresa existente"""
        try:
            # Verificar si la empresa existe
            existing_empresa = self.empresa_repository.find_by_id(empresa_id)
            if not existing_empresa:
                return {
                    'success': False,
                    'errors': ['Empresa no encontrada']
                }
            
            # Si se proporciona super_admin_id, verificar que sea el creador
            if super_admin_id:
                if isinstance(super_admin_id, str):
                    super_admin_id = ObjectId(super_admin_id)
                
                if existing_empresa.creado_por != super_admin_id:
                    return {
                        'success': False,
                        'errors': ['No tienes permisos para modificar esta empresa']
                    }
            
            # Crear objeto Empresa con datos actualizados
            updated_empresa = Empresa(
                nombre=empresa_data.get('nombre', existing_empresa.nombre),
                descripcion=empresa_data.get('descripcion', existing_empresa.descripcion),
                ubicacion=empresa_data.get('ubicacion', existing_empresa.ubicacion),
                email=empresa_data.get('email', existing_empresa.email),
                password_hash=existing_empresa.password_hash,
                creado_por=existing_empresa.creado_por,
                _id=existing_empresa._id
            )
            
            # Mantener datos originales
            updated_empresa.fecha_creacion = existing_empresa.fecha_creacion
            updated_empresa.activa = existing_empresa.activa

            new_password = empresa_data.get('password')
            if new_password:
                updated_empresa.password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Validar datos
            validation_errors = updated_empresa.validate()
            if validation_errors:
                return {
                    'success': False,
                    'errors': validation_errors
                }
            
            # Verificar si el nombre ya existe (solo si cambió)
            if updated_empresa.nombre.lower() != existing_empresa.nombre.lower():
                nombre_exists = self.empresa_repository.find_by_nombre(updated_empresa.nombre)
                if nombre_exists:
                    return {
                        'success': False,
                        'errors': ['Ya existe una empresa con ese nombre']
                    }

            if updated_empresa.email != existing_empresa.email:
                email_exists = self.empresa_repository.find_by_email(updated_empresa.email)
                if email_exists:
                    return {
                        'success': False,
                        'errors': ['Ya existe una empresa con ese email']
                    }
            
            # Actualizar empresa
            result = self.empresa_repository.update(empresa_id, updated_empresa)
            if result:
                return {
                    'success': True,
                    'data': result.to_json(),
                    'message': 'Empresa actualizada exitosamente'
                }
            else:
                return {
                    'success': False,
                    'errors': ['Error actualizando empresa']
                }
                
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            }
    
    def delete_empresa(self, empresa_id, super_admin_id=None):
        """Elimina una empresa (soft delete)"""
        try:
            # Verificar si la empresa existe
            existing_empresa = self.empresa_repository.find_by_id(empresa_id)
            if not existing_empresa:
                return {
                    'success': False,
                    'errors': ['Empresa no encontrada']
                }
            
            # Si se proporciona super_admin_id, verificar que sea el creador
            if super_admin_id:
                if isinstance(super_admin_id, str):
                    super_admin_id = ObjectId(super_admin_id)
                
                if existing_empresa.creado_por != super_admin_id:
                    return {
                        'success': False,
                        'errors': ['No tienes permisos para eliminar esta empresa']
                    }
            
            # Eliminar empresa (soft delete)
            deleted = self.empresa_repository.soft_delete(empresa_id)
            if deleted:
                return {
                    'success': True,
                    'message': 'Empresa eliminada correctamente'
                }
            else:
                return {
                    'success': False,
                    'errors': ['Error eliminando empresa']
                }
                
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            }
    
    def search_empresas_by_ubicacion(self, ubicacion):
        """Busca empresas por ubicación"""
        try:
            empresas = self.empresa_repository.search_by_ubicacion(ubicacion)
            empresas_json = [empresa.to_json() for empresa in empresas]
            return {
                'success': True,
                'data': empresas_json,
                'count': len(empresas_json)
            }
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            }
    
    def get_empresa_stats(self):
        """Obtiene estadísticas de empresas"""
        try:
            total_activas = self.empresa_repository.count(include_inactive=False)
            total_inactivas = self.empresa_repository.count(include_inactive=True) - total_activas
            
            return {
                'success': True,
                'data': {
                    'total_activas': total_activas,
                    'total_inactivas': total_inactivas,
                    'total_general': total_activas + total_inactivas
                }
            }
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            }