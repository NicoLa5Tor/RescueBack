from bson import ObjectId
from models.user import User
from repositories.user_repository import UserRepository
from repositories.empresa_repository import EmpresaRepository

class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.empresa_repository = EmpresaRepository()
    
    def create_user(self, user_data):
        """Crea un nuevo usuario con validaciones"""
        try:
            # Crear objeto User y validar ID de empresa
            try:
                user = User(
                    name=user_data.get('name'),
                    email=user_data.get('email'),
                    age=user_data.get('age'),
                    empresa_id=user_data.get('empresa_id'),
                    telefono=user_data.get('telefono'),
                    whatsapp_verify=user_data.get('whatsapp_verify', False)
                )
            except Exception:
                return {
                    'success': False,
                    'errors': ['El ID de la empresa no es válido']
                }

            # Verificar que la empresa exista
            if user.empresa_id:
                empresa = self.empresa_repository.find_by_id(user.empresa_id)
                if not empresa:
                    return {
                        'success': False,
                        'errors': ['La empresa especificada no existe']
                    }
            
            # Validar datos
            validation_errors = user.validate()
            if validation_errors:
                return {
                    'success': False,
                    'errors': validation_errors
                }
            
            # Verificar si el email ya existe
            existing_user = self.user_repository.find_by_email(user.email)
            if existing_user:
                return {
                    'success': False,
                    'errors': ['El email ya está registrado']
                }
            
            # Crear usuario
            created_user = self.user_repository.create(user)
            return {
                'success': True,
                'data': created_user.to_json()
            }
            
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            }
    
    def get_user_by_id(self, user_id):
        """Obtiene un usuario por ID"""
        try:
            user = self.user_repository.find_by_id(user_id)
            if user:
                return {
                    'success': True,
                    'data': user.to_json()
                }
            else:
                return {
                    'success': False,
                    'errors': ['Usuario no encontrado']
                }
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            }

    def get_user_by_phone(self, telefono):
        """Obtiene un usuario por número de teléfono"""
        try:
            user = self.user_repository.find_by_telefono(telefono)
            if user:
                return {
                    'success': True,
                    'data': user.to_json()
                }
            else:
                return {
                    'success': False,
                    'errors': ['Usuario no encontrado']
                }
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            }
    
    def get_all_users(self):
        """Obtiene todos los usuarios"""
        try:
            users = self.user_repository.find_all()
            users_json = [user.to_json() for user in users]
            return {
                'success': True,
                'data': users_json,
                'count': len(users_json)
            }
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            }
    
    def update_user(self, user_id, user_data):
        """Actualiza un usuario existente"""
        try:
            # Verificar si el usuario existe
            existing_user = self.user_repository.find_by_id(user_id)
            if not existing_user:
                return {
                    'success': False,
                    'errors': ['Usuario no encontrado']
                }
            
            # Determinar el ID de la empresa a usar y verificarlo
            new_empresa_id = user_data.get('empresa_id', existing_user.empresa_id)
            if new_empresa_id is not None:
                try:
                    empresa_id_obj = ObjectId(str(new_empresa_id))
                except Exception:
                    return {
                        'success': False,
                        'errors': ['El ID de la empresa no es válido']
                    }
                empresa = self.empresa_repository.find_by_id(empresa_id_obj)
                if not empresa:
                    return {
                        'success': False,
                        'errors': ['La empresa especificada no existe']
                    }
            else:
                empresa_id_obj = None

            # Crear objeto User con datos actualizados
            updated_user = User(
                name=user_data.get('name', existing_user.name),
                email=user_data.get('email', existing_user.email),
                age=user_data.get('age', existing_user.age),
                empresa_id=empresa_id_obj,
                telefono=user_data.get('telefono', existing_user.telefono),
                whatsapp_verify=user_data.get('whatsapp_verify', existing_user.whatsapp_verify),
                _id=existing_user._id
            )
            
            # Validar datos
            validation_errors = updated_user.validate()
            if validation_errors:
                return {
                    'success': False,
                    'errors': validation_errors
                }
            
            # Verificar si el email ya existe (solo si cambió)
            if updated_user.email != existing_user.email:
                email_exists = self.user_repository.find_by_email(updated_user.email)
                if email_exists:
                    return {
                        'success': False,
                        'errors': ['El email ya está registrado']
                    }
            
            # Actualizar usuario
            result = self.user_repository.update(user_id, updated_user)
            if result:
                return {
                    'success': True,
                    'data': result.to_json()
                }
            else:
                return {
                    'success': False,
                    'errors': ['Error actualizando usuario']
                }
                
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            }
    
    def delete_user(self, user_id):
        """Elimina un usuario"""
        try:
            # Verificar si el usuario existe
            existing_user = self.user_repository.find_by_id(user_id)
            if not existing_user:
                return {
                    'success': False,
                    'errors': ['Usuario no encontrado']
                }
            
            # Eliminar usuario
            deleted = self.user_repository.delete(user_id)
            if deleted:
                return {
                    'success': True,
                    'message': 'Usuario eliminado correctamente'
                }
            else:
                return {
                    'success': False,
                    'errors': ['Error eliminando usuario']
                }
                
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            }
    
    def get_users_by_age_range(self, min_age, max_age):
        """Obtiene usuarios por rango de edad"""
        try:
            users = self.user_repository.find_by_age_range(min_age, max_age)
            users_json = [user.to_json() for user in users]
            return {
                'success': True,
                'data': users_json,
                'count': len(users_json)
            }
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            
