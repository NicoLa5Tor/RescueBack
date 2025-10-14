from models.tipo_alarma import TipoAlarma
from repositories.tipo_alarma_repository import TipoAlarmaRepository
from repositories.empresa_repository import EmpresaRepository
from bson import ObjectId
import base64
import io

class TipoAlarmaService:
    """Servicio para gestionar tipos de alarma con lógica de negocio"""
    
    def __init__(self):
        self.tipo_alarma_repo = TipoAlarmaRepository()
        self.empresa_repo = EmpresaRepository()
    
    def create_tipo_alarma(self, tipo_alarma_data):
        """
        Crea un nuevo tipo de alarma
        
        Args:
            tipo_alarma_data (dict): Datos del tipo de alarma
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            # Validar datos requeridos
            if not tipo_alarma_data.get('nombre'):
                return {'success': False, 'error': 'El nombre es obligatorio'}
            
            if not tipo_alarma_data.get('descripcion'):
                return {'success': False, 'error': 'La descripción es obligatoria'}
            
            if not tipo_alarma_data.get('tipo_alerta'):
                return {'success': False, 'error': 'El tipo de alerta es obligatorio'}
            
            if not tipo_alarma_data.get('color_alerta'):
                return {'success': False, 'error': 'El color de alerta es obligatorio'}
            
            # Validar tipo de alerta
            if tipo_alarma_data['tipo_alerta'] not in TipoAlarma.TIPOS_ALERTA.values():
                return {'success': False, 'error': f'Tipo de alerta inválido. Debe ser uno de: {", ".join(TipoAlarma.TIPOS_ALERTA.values())}'}
            
            # Validar empresa si se proporciona
            empresa_id = tipo_alarma_data.get('empresa_id')
            if empresa_id:
                if not self.tipo_alarma_repo.verify_empresa_exists(empresa_id):
                    return {'success': False, 'error': 'La empresa especificada no existe'}
                
                # Verificar duplicados para la empresa
                if self.tipo_alarma_repo.check_duplicate_name(tipo_alarma_data['nombre'], empresa_id):
                    return {'success': False, 'error': 'Ya existe un tipo de alarma con ese nombre para esta empresa'}
            
            # Validar imagen si se proporciona
            imagen_base64 = tipo_alarma_data.get('imagen_base64')
            if imagen_base64:
                validation_result = self._validate_image_base64(imagen_base64)
                if not validation_result['valid']:
                    return {'success': False, 'error': validation_result['error']}
            
            # Crear objeto TipoAlarma
            tipo_alarma = TipoAlarma(
                nombre=tipo_alarma_data['nombre'],
                descripcion=tipo_alarma_data['descripcion'],
                tipo_alerta=tipo_alarma_data['tipo_alerta'],
                color_alerta=tipo_alarma_data['color_alerta'],
                imagen_base64=imagen_base64,
                recomendaciones=tipo_alarma_data.get('recomendaciones', []),
                implementos_necesarios=tipo_alarma_data.get('implementos_necesarios', []),
                empresa_id=empresa_id
            )
            
            # Validar modelo
            errors = tipo_alarma.validate()
            if errors:
                return {'success': False, 'error': '; '.join(errors)}
            
            # Crear en la base de datos
            tipo_alarma_creado = self.tipo_alarma_repo.create_tipo_alarma(tipo_alarma)
            
            return {
                'success': True,
                'data': tipo_alarma_creado.to_json(),
                'message': 'Tipo de alarma creado exitosamente'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Error interno: {str(e)}'}
    
    def get_tipo_alarma_by_id(self, tipo_alarma_id):
        """
        Obtiene un tipo de alarma por su ID
        
        Args:
            tipo_alarma_id (str): ID del tipo de alarma
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            if not ObjectId.is_valid(tipo_alarma_id):
                return {'success': False, 'error': 'ID inválido'}
            
            tipo_alarma = self.tipo_alarma_repo.get_tipo_alarma_by_id(tipo_alarma_id)
            
            if not tipo_alarma:
                return {'success': False, 'error': 'Tipo de alarma no encontrado'}
            
            return {
                'success': True,
                'data': tipo_alarma.to_json()
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Error interno: {str(e)}'}
    
    def get_tipos_alarma_by_empresa(self, empresa_id, page=1, limit=50):
        """
        Obtiene tipos de alarma por empresa
        
        Args:
            empresa_id (str): ID de la empresa
            page (int): Página
            limit (int): Límite por página
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            if not ObjectId.is_valid(empresa_id):
                return {'success': False, 'error': 'ID de empresa inválido'}
            
            if not self.tipo_alarma_repo.verify_empresa_exists(empresa_id):
                return {'success': False, 'error': 'La empresa no existe'}
            
            tipos_alarma, total = self.tipo_alarma_repo.get_tipos_alarma_by_empresa(empresa_id, page, limit)
            
            return {
                'success': True,
                'data': [tipo.to_json() for tipo in tipos_alarma],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Error interno: {str(e)}'}
    
    def get_tipos_alarma_by_tipo_alerta(self, tipo_alerta, page=1, limit=50):
        """
        Obtiene tipos de alarma por tipo de alerta
        
        Args:
            tipo_alerta (str): Tipo de alerta
            page (int): Página
            limit (int): Límite por página
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            if tipo_alerta not in TipoAlarma.TIPOS_ALERTA.values():
                return {'success': False, 'error': f'Tipo de alerta inválido. Debe ser uno de: {", ".join(TipoAlarma.TIPOS_ALERTA.values())}'}
            
            tipos_alarma, total = self.tipo_alarma_repo.get_tipos_alarma_by_tipo_alerta(tipo_alerta, page, limit)
            
            return {
                'success': True,
                'data': [tipo.to_json() for tipo in tipos_alarma],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Error interno: {str(e)}'}
    
    def get_all_tipos_alarma(self, page=1, limit=50):
        """
        Obtiene todos los tipos de alarma

        Args:
            page (int): Página
            limit (int): Límite por página

        Returns:
            dict: Resultado de la operación
        """
        try:
            tipos_alarma, total = self.tipo_alarma_repo.get_all_tipos_alarma(page, limit)

            return {
                'success': True,
                'data': [tipo.to_json() for tipo in tipos_alarma],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit
                }
            }

        except Exception as e:
            return {'success': False, 'error': f'Error interno: {str(e)}'}

    def get_active_tipos_alarma(self, page=1, limit=50):
        """
        Obtiene solo tipos de alarma activos

        Args:
            page (int): Página
            limit (int): Límite por página

        Returns:
            dict: Resultado de la operación
        """
        try:
            tipos_alarma, total = self.tipo_alarma_repo.get_active_tipos_alarma(page, limit)

            return {
                'success': True,
                'data': [tipo.to_json() for tipo in tipos_alarma],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit
                }
            }

        except Exception as e:
            return {'success': False, 'error': f'Error interno: {str(e)}'}

    def get_inactive_tipos_alarma(self, page=1, limit=50):
        """
        Obtiene solo tipos de alarma inactivos

        Args:
            page (int): Página
            limit (int): Límite por página

        Returns:
            dict: Resultado de la operación
        """
        try:
            tipos_alarma, total = self.tipo_alarma_repo.get_inactive_tipos_alarma(page, limit)

            return {
                'success': True,
                'data': [tipo.to_json() for tipo in tipos_alarma],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit
                }
            }

        except Exception as e:
            return {'success': False, 'error': f'Error interno: {str(e)}'}
    
    def update_tipo_alarma(self, tipo_alarma_id, update_data):
        """
        Actualiza un tipo de alarma
        
        Args:
            tipo_alarma_id (str): ID del tipo de alarma
            update_data (dict): Datos a actualizar
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            if not ObjectId.is_valid(tipo_alarma_id):
                return {'success': False, 'error': 'ID inválido'}
            
            # Obtener tipo de alarma existente
            tipo_alarma = self.tipo_alarma_repo.get_tipo_alarma_by_id(tipo_alarma_id)
            if not tipo_alarma:
                return {'success': False, 'error': 'Tipo de alarma no encontrado'}
            
            # Actualizar campos
            if 'nombre' in update_data:
                # Verificar duplicados si se cambia el nombre
                if (update_data['nombre'] != tipo_alarma.nombre and 
                    tipo_alarma.empresa_id and 
                    self.tipo_alarma_repo.check_duplicate_name(update_data['nombre'], tipo_alarma.empresa_id, tipo_alarma_id)):
                    return {'success': False, 'error': 'Ya existe un tipo de alarma con ese nombre para esta empresa'}
                tipo_alarma.nombre = update_data['nombre']
            
            if 'descripcion' in update_data:
                tipo_alarma.descripcion = update_data['descripcion']
            
            if 'tipo_alerta' in update_data:
                if update_data['tipo_alerta'] not in TipoAlarma.TIPOS_ALERTA.values():
                    return {'success': False, 'error': f'Tipo de alerta inválido. Debe ser uno de: {", ".join(TipoAlarma.TIPOS_ALERTA.values())}'}
                tipo_alarma.tipo_alerta = update_data['tipo_alerta']
            
            if 'color_alerta' in update_data:
                tipo_alarma.color_alerta = update_data['color_alerta']
            
            if 'imagen_base64' in update_data:
                imagen_base64 = update_data['imagen_base64']
                if imagen_base64:
                    validation_result = self._validate_image_base64(imagen_base64)
                    if not validation_result['valid']:
                        return {'success': False, 'error': validation_result['error']}
                tipo_alarma.imagen_base64 = imagen_base64
            
            if 'recomendaciones' in update_data:
                tipo_alarma.recomendaciones = update_data['recomendaciones']
            
            if 'implementos_necesarios' in update_data:
                tipo_alarma.implementos_necesarios = update_data['implementos_necesarios']
            
            # Validar modelo actualizado
            errors = tipo_alarma.validate()
            if errors:
                return {'success': False, 'error': '; '.join(errors)}
            
            # Actualizar en la base de datos
            if self.tipo_alarma_repo.update_tipo_alarma(tipo_alarma_id, tipo_alarma):
                return {
                    'success': True,
                    'data': tipo_alarma.to_json(),
                    'message': 'Tipo de alarma actualizado exitosamente'
                }
            else:
                return {'success': False, 'error': 'No se pudo actualizar el tipo de alarma'}
            
        except Exception as e:
            return {'success': False, 'error': f'Error interno: {str(e)}'}
    
    def delete_tipo_alarma(self, tipo_alarma_id):
        """
        Elimina un tipo de alarma
        
        Args:
            tipo_alarma_id (str): ID del tipo de alarma
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            if not ObjectId.is_valid(tipo_alarma_id):
                return {'success': False, 'error': 'ID inválido'}
            
            # Verificar que existe
            tipo_alarma = self.tipo_alarma_repo.get_tipo_alarma_by_id(tipo_alarma_id)
            if not tipo_alarma:
                return {'success': False, 'error': 'Tipo de alarma no encontrado'}
            
            # Eliminar
            if self.tipo_alarma_repo.delete_tipo_alarma(tipo_alarma_id):
                return {
                    'success': True,
                    'message': 'Tipo de alarma eliminado exitosamente'
                }
            else:
                return {'success': False, 'error': 'No se pudo eliminar el tipo de alarma'}
            
        except Exception as e:
            return {'success': False, 'error': f'Error interno: {str(e)}'}
    
    def toggle_tipo_alarma_status(self, tipo_alarma_id):
        """
        Alterna el estado activo de un tipo de alarma
        
        Args:
            tipo_alarma_id (str): ID del tipo de alarma
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            if not ObjectId.is_valid(tipo_alarma_id):
                return {'success': False, 'error': 'ID inválido'}
            
            tipo_alarma = self.tipo_alarma_repo.get_tipo_alarma_by_id(tipo_alarma_id)
            if not tipo_alarma:
                return {'success': False, 'error': 'Tipo de alarma no encontrado'}
            
            if self.tipo_alarma_repo.toggle_tipo_alarma_status(tipo_alarma_id):
                new_status = not tipo_alarma.activo
                return {
                    'success': True,
                    'data': {'activo': new_status},
                    'message': f'Tipo de alarma {"activado" if new_status else "desactivado"} exitosamente'
                }
            else:
                return {'success': False, 'error': 'No se pudo cambiar el estado del tipo de alarma'}
            
        except Exception as e:
            return {'success': False, 'error': f'Error interno: {str(e)}'}
    
    def get_tipos_alarma_stats(self):
        """
        Obtiene estadísticas de tipos de alarma
        
        Returns:
            dict: Resultado de la operación
        """
        try:
            stats = self.tipo_alarma_repo.get_tipos_alarma_stats()
            return {
                'success': True,
                'data': stats
            }
        except Exception as e:
            return {'success': False, 'error': f'Error interno: {str(e)}'}
    
    def search_tipos_alarma(self, search_term, page=1, limit=50):
        """
        Busca tipos de alarma por nombre o descripción
        
        Args:
            search_term (str): Término de búsqueda
            page (int): Página
            limit (int): Límite por página
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            if not search_term or len(search_term.strip()) < 2:
                return {'success': False, 'error': 'El término de búsqueda debe tener al menos 2 caracteres'}
            
            tipos_alarma, total = self.tipo_alarma_repo.search_tipos_alarma(search_term.strip(), page, limit)
            
            return {
                'success': True,
                'data': [tipo.to_json() for tipo in tipos_alarma],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Error interno: {str(e)}'}
    
    def get_tipos_alerta_disponibles(self):
        """
        Obtiene los tipos de alerta disponibles
        
        Returns:
            dict: Resultado de la operación
        """
        try:
            return {
                'success': True,
                'data': list(TipoAlarma.TIPOS_ALERTA.values())
            }
        except Exception as e:
            return {'success': False, 'error': f'Error interno: {str(e)}'}
    
    def _validate_image_base64(self, image_base64):
        """
        Valida una imagen en formato base64
        
        Args:
            image_base64 (str): Imagen en base64
            
        Returns:
            dict: Resultado de la validación
        """
        try:
            # Verificar formato base64
            if not image_base64.startswith('data:image/'):
                return {'valid': False, 'error': 'La imagen debe estar en formato base64 con prefijo data:image/'}
            
            # Extraer datos de la imagen
            header, data = image_base64.split(',', 1)
            
            # Verificar tipo de imagen desde el header
            allowed_headers = [
                'data:image/jpeg',
                'data:image/jpg', 
                'data:image/png',
                'data:image/gif',
                'data:image/webp'
            ]
            
            if not any(header.startswith(allowed_header) for allowed_header in allowed_headers):
                return {'valid': False, 'error': f'Tipo de imagen no permitido. Permitidos: jpeg, jpg, png, gif, webp'}
            
            # Decodificar base64
            try:
                image_data = base64.b64decode(data)
            except Exception:
                return {'valid': False, 'error': 'Los datos base64 no son válidos'}
            
            # Verificar que los datos no estén vacíos
            if len(image_data) == 0:
                return {'valid': False, 'error': 'Los datos de la imagen están vacíos'}
            
            # Verificar tamaño (10MB máximo)
            max_size = 10 * 1024 * 1024  # 10MB
            if len(image_data) > max_size:
                return {'valid': False, 'error': f'La imagen no puede exceder {max_size / (1024 * 1024):.0f}MB'}
            
            # Verificar headers básicos de imagen
            if header.startswith('data:image/jpeg') or header.startswith('data:image/jpg'):
                if not (image_data.startswith(b'\xff\xd8\xff') or image_data.startswith(b'\xff\xd8')):
                    return {'valid': False, 'error': 'Los datos no corresponden a una imagen JPEG válida'}
            elif header.startswith('data:image/png'):
                if not image_data.startswith(b'\x89PNG\r\n\x1a\n'):
                    return {'valid': False, 'error': 'Los datos no corresponden a una imagen PNG válida'}
            elif header.startswith('data:image/gif'):
                if not (image_data.startswith(b'GIF87a') or image_data.startswith(b'GIF89a')):
                    return {'valid': False, 'error': 'Los datos no corresponden a una imagen GIF válida'}
            elif header.startswith('data:image/webp'):
                if not image_data.startswith(b'RIFF') or b'WEBP' not in image_data[:12]:
                    return {'valid': False, 'error': 'Los datos no corresponden a una imagen WebP válida'}
            
            return {'valid': True}
            
        except Exception as e:
            return {'valid': False, 'error': f'Error validando imagen: {str(e)}'}
