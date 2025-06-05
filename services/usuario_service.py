from bson import ObjectId
from models.usuario import Usuario
from repositories.usuario_repository import UsuarioRepository
from repositories.empresa_repository import EmpresaRepository

class UsuarioService:
    def __init__(self):
        self.usuario_repository = UsuarioRepository()
        self.empresa_repository = EmpresaRepository()
    
    def create_usuario_for_empresa(self, empresa_id, usuario_data):
        """Crea un usuario para una empresa específica"""
        try:
            # 1. Verificar que la empresa existe
            if isinstance(empresa_id, str):
                try:
                    empresa_id_obj = ObjectId(empresa_id)
                except Exception:
                    return {
                        'success': False,
                        'errors': ['El ID de empresa no es válido'],
                        'status_code': 400
                    }
            else:
                empresa_id_obj = empresa_id
            
            empresa = self.empresa_repository.find_by_id(empresa_id_obj)
            if not empresa:
                return {
                    'success': False,
                    'errors': ['La empresa especificada no existe'],
                    'status_code': 403
                }
            
            # 2. Crear objeto Usuario
            usuario = Usuario(
                nombre=usuario_data.get('nombre'),
                cedula=usuario_data.get('cedula'),
                rol=usuario_data.get('rol'),
                empresa_id=empresa_id_obj
            )
            
            # 3. Validar datos del usuario
            validation_errors = usuario.validate()
            if validation_errors:
                return {
                    'success': False,
                    'errors': validation_errors,
                    'status_code': 400
                }
            
            # 4. Verificar que no exista un usuario con la misma cédula en la empresa
            existing_usuario = self.usuario_repository.find_by_cedula_and_empresa(
                usuario.cedula, empresa_id_obj
            )
            if existing_usuario:
                return {
                    'success': False,
                    'errors': ['Ya existe un usuario con esa cédula en esta empresa'],
                    'status_code': 400
                }
            
            # 5. Crear usuario
            created_usuario = self.usuario_repository.create(usuario)
            
            # 6. Incluir información de la empresa en la respuesta
            response_data = created_usuario.to_json()
            response_data['empresa'] = {
                'id': str(empresa.empresa_id) if hasattr(empresa, 'empresa_id') else str(empresa._id),
                'nombre': empresa.nombre
            }
            
            return {
                'success': True,
                'data': response_data,
                'message': f'Usuario creado exitosamente para la empresa {empresa.nombre}',
                'status_code': 201
            }
            
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)],
                'status_code': 500
            }
    
    def get_usuarios_by_empresa(self, empresa_id):
        """Obtiene todos los usuarios de una empresa"""
        try:
            # Verificar que la empresa existe
            if isinstance(empresa_id, str):
                empresa_id_obj = ObjectId(empresa_id)
            else:
                empresa_id_obj = empresa_id
            
            empresa = self.empresa_repository.find_by_id(empresa_id_obj)
            if not empresa:
                return {
                    'success': False,
                    'errors': ['La empresa especificada no existe'],
                    'status_code': 404
                }
            
            usuarios = self.usuario_repository.find_by_empresa(empresa_id_obj)
            usuarios_json = [usuario.to_json() for usuario in usuarios]
            
            return {
                'success': True,
                'data': usuarios_json,
                'count': len(usuarios_json),
                'empresa': {
                    'id': str(empresa._id),
                    'nombre': empresa.nombre
                },
                'status_code': 200
            }
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)],
                'status_code': 500
            }
    
    def get_usuario_by_id_and_empresa(self, usuario_id, empresa_id):
        """Obtiene un usuario específico de una empresa"""
        try:
            # Verificar que la empresa existe
            if isinstance(empresa_id, str):
                empresa_id_obj = ObjectId(empresa_id)
            else:
                empresa_id_obj = empresa_id
            
            empresa = self.empresa_repository.find_by_id(empresa_id_obj)
            if not empresa:
                return {
                    'success': False,
                    'errors': ['La empresa especificada no existe'],
                    'status_code': 404
                }
            
            # Buscar usuario
            usuario = self.usuario_repository.find_by_id(usuario_id)
            if not usuario:
                return {
                    'success': False,
                    'errors': ['Usuario no encontrado'],
                    'status_code': 404
                }
            
            # Verificar que el usuario pertenece a la empresa
            if usuario.empresa_id != empresa_id_obj:
                return {
                    'success': False,
                    'errors': ['El usuario no pertenece a esta empresa'],
                    'status_code': 403
                }
            
            response_data = usuario.to_json()
            response_data['empresa'] = {
                'id': str(empresa._id),
                'nombre': empresa.nombre
            }
            
            return {
                'success': True,
                'data': response_data,
                'status_code': 200
            }
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)],
                'status_code': 500
            }
    
    def update_usuario_for_empresa(self, usuario_id, empresa_id, usuario_data):
        """Actualiza un usuario de una empresa específica"""
        try:
            # Verificar que la empresa y usuario existen
            existing_result = self.get_usuario_by_id_and_empresa(usuario_id, empresa_id)
            if not existing_result['success']:
                return existing_result
            
            existing_usuario = self.usuario_repository.find_by_id(usuario_id)
            
            # Crear objeto Usuario con datos actualizados
            updated_usuario = Usuario(
                nombre=usuario_data.get('nombre', existing_usuario.nombre),
                cedula=usuario_data.get('cedula', existing_usuario.cedula),
                rol=usuario_data.get('rol', existing_usuario.rol),
                empresa_id=existing_usuario.empresa_id,
                _id=existing_usuario._id
            )
            
            # Mantener datos originales
            updated_usuario.fecha_creacion = existing_usuario.fecha_creacion
            updated_usuario.activo = existing_usuario.activo
            
            # Validar datos
            validation_errors = updated_usuario.validate()
            if validation_errors:
                return {
                    'success': False,
                    'errors': validation_errors,
                    'status_code': 400
                }
            
            # Verificar duplicado de cédula (solo si cambió)
            if updated_usuario.cedula != existing_usuario.cedula:
                cedula_exists = self.usuario_repository.find_by_cedula_and_empresa(
                    updated_usuario.cedula, existing_usuario.empresa_id
                )
                if cedula_exists:
                    return {
                        'success': False,
                        'errors': ['Ya existe un usuario con esa cédula en esta empresa'],
                        'status_code': 400
                    }
            
            # Actualizar usuario
            result = self.usuario_repository.update(usuario_id, updated_usuario)
            if result:
                response_data = result.to_json()
                empresa = self.empresa_repository.find_by_id(result.empresa_id)
                response_data['empresa'] = {
                    'id': str(empresa._id),
                    'nombre': empresa.nombre
                }
                
                return {
                    'success': True,
                    'data': response_data,
                    'message': 'Usuario actualizado exitosamente',
                    'status_code': 200
                }
            else:
                return {
                    'success': False,
                    'errors': ['Error actualizando usuario'],
                    'status_code': 500
                }
                
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)],
                'status_code': 500
            }
    
    def delete_usuario_for_empresa(self, usuario_id, empresa_id):
        """Elimina un usuario de una empresa específica"""
        try:
            # Verificar que la empresa y usuario existen
            existing_result = self.get_usuario_by_id_and_empresa(usuario_id, empresa_id)
            if not existing_result['success']:
                return existing_result
            
            # Eliminar usuario (soft delete)
            deleted = self.usuario_repository.soft_delete(usuario_id)
            if deleted:
                return {
                    'success': True,
                    'message': 'Usuario eliminado correctamente',
                    'status_code': 200
                }
            else:
                return {
                    'success': False,
                    'errors': ['Error eliminando usuario'],
                    'status_code': 500
                }
                
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)],
                'status_code': 500
            }