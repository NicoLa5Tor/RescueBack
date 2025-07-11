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
            if not password:
                return {'success': False, 'errors': ['La contraseña es obligatoria']}

            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Validar tipo_empresa_id si se proporciona
            tipo_empresa_id = empresa_data.get('tipo_empresa_id')
            if tipo_empresa_id:
                try:
                    if isinstance(tipo_empresa_id, str):
                        tipo_empresa_id = ObjectId(tipo_empresa_id)
                except Exception:
                    return {
                        'success': False,
                        'errors': ['El ID del tipo de empresa no es válido']
                    }

            empresa = Empresa(
                nombre=empresa_data.get('nombre'),
                descripcion=empresa_data.get('descripcion'),
                ubicacion=empresa_data.get('ubicacion'),
                creado_por=super_admin_id,
                username=empresa_data.get('username'),
                email=empresa_data.get('email'),
                password_hash=password_hash,
                sedes=empresa_data.get('sedes'),
                roles=empresa_data.get('roles', []),
                tipo_empresa_id=tipo_empresa_id
            )
            
            # Validar datos
            validation_errors = empresa.validate()
            if validation_errors:
                return {
                    'success': False,
                    'errors': validation_errors
                }
            
            # Verificar duplicados
            if self.empresa_repository.find_by_nombre(empresa.nombre):
                return {
                    'success': False,
                    'errors': ['Ya existe una empresa con ese nombre']
                }
            if self.empresa_repository.find_by_username(empresa.username):
                return {
                    'success': False,
                    'errors': ['El nombre de usuario ya está en uso']
                }
            if self.empresa_repository.find_by_email(empresa.email):
                return {
                    'success': False,
                    'errors': ['El correo ya está en uso']
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
    
    def get_empresa_by_id_including_inactive(self, empresa_id):
        """Obtiene una empresa por ID incluyendo inactivas (para admins)"""
        try:
            empresa = self.empresa_repository.find_by_id_including_inactive(empresa_id)
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
    
    def update_empresa(self, empresa_id, empresa_data, super_admin_id=None):
        """Actualiza una empresa existente"""
        try:
            # Verificar si la empresa existe (incluyendo inactivas)
            existing_empresa = self.empresa_repository.find_by_id_including_inactive(empresa_id)
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
            
            # Preparar password
            new_password = empresa_data.get('password')
            password_hash = existing_empresa.password_hash
            if new_password:
                password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Validar tipo_empresa_id si se proporciona para actualización
            tipo_empresa_id = empresa_data.get('tipo_empresa_id', existing_empresa.tipo_empresa_id)
            if tipo_empresa_id and isinstance(tipo_empresa_id, str):
                try:
                    tipo_empresa_id = ObjectId(tipo_empresa_id)
                except Exception:
                    return {
                        'success': False,
                        'errors': ['El ID del tipo de empresa no es válido']
                    }

            # Crear objeto Empresa con datos actualizados
            updated_empresa = Empresa(
                nombre=empresa_data.get('nombre', existing_empresa.nombre),
                descripcion=empresa_data.get('descripcion', existing_empresa.descripcion),
                ubicacion=empresa_data.get('ubicacion', existing_empresa.ubicacion),
                creado_por=existing_empresa.creado_por,
                username=empresa_data.get('username', existing_empresa.username),
                email=empresa_data.get('email', existing_empresa.email),
                password_hash=password_hash,
                sedes=empresa_data.get('sedes', existing_empresa.sedes),
                roles=empresa_data.get('roles', existing_empresa.roles),
                tipo_empresa_id=tipo_empresa_id,
                _id=existing_empresa._id,
                activa=existing_empresa.activa,
            )

            # Mantener datos originales
            updated_empresa.fecha_creacion = existing_empresa.fecha_creacion
            updated_empresa.last_login = existing_empresa.last_login
            
            # Validar datos
            validation_errors = updated_empresa.validate()
            if validation_errors:
                return {
                    'success': False,
                    'errors': validation_errors
                }
            
            # Verificar si el nombre ya existe (solo si cambió)
            if updated_empresa.nombre.lower() != existing_empresa.nombre.lower():
                nombre_exists = self.empresa_repository.find_by_nombre_excluding_id(
                    updated_empresa.nombre, empresa_id
                )
                if nombre_exists:
                    return {
                        'success': False,
                        'errors': ['Ya existe una empresa con ese nombre']
                    }

            if updated_empresa.username != existing_empresa.username:
                username_exists = self.empresa_repository.find_by_username_excluding_id(
                    updated_empresa.username, empresa_id
                )
                if username_exists:
                    return {
                        'success': False,
                        'errors': ['El nombre de usuario ya está en uso']
                    }

            if updated_empresa.email != existing_empresa.email:
                email_exists = self.empresa_repository.find_by_email_excluding_id(
                    updated_empresa.email, empresa_id
                )
                if email_exists:
                    return {
                        'success': False,
                        'errors': ['El correo ya está en uso']
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
            # Verificar si la empresa existe (incluyendo inactivas)
            existing_empresa = self.empresa_repository.find_by_id_including_inactive(empresa_id)
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
    
    def toggle_empresa_status(self, empresa_id, activa, super_admin_id=None):
        """Activar o desactivar empresa"""
        try:
            # Verificar si la empresa existe (incluyendo inactivas)
            existing_empresa = self.empresa_repository.find_by_id_including_inactive(empresa_id)
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
            
            # Actualizar solo el campo activa
            existing_empresa.activa = activa
            existing_empresa.update_timestamp()
            
            updated = self.empresa_repository.update(empresa_id, existing_empresa)
            if updated:
                status_text = "activada" if activa else "desactivada"
                return {
                    'success': True, 
                    'data': updated.to_json(),
                    'message': f'Empresa {status_text} exitosamente'
                }
            return {
                'success': False, 
                'errors': ['Error al actualizar el estado de la empresa']
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