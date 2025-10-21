from models.tipo_alarma import TipoAlarma
from repositories.tipo_alarma_repository import TipoAlarmaRepository
from repositories.empresa_repository import EmpresaRepository
from bson import ObjectId

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
                validation_result = self._validate_image_value(imagen_base64)
                if not validation_result['valid']:
                    return {'success': False, 'error': validation_result['error']}
            
            # Normalizar color en mayúsculas
            tipo_alarma_data['color_alerta'] = tipo_alarma_data['color_alerta'].strip().upper()

            # Crear objeto TipoAlarma
            tipo_alarma = TipoAlarma(
                nombre=tipo_alarma_data['nombre'],
                descripcion=tipo_alarma_data['descripcion'],
                tipo_alerta=tipo_alarma_data['tipo_alerta'],
                color_alerta=tipo_alarma_data['color_alerta'],
                imagen_base64=imagen_base64,
                sonido_link=tipo_alarma_data.get('sonido_link'),
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

    def get_tipos_alarma_by_empresa_full(self, empresa_id, solo_activos=False):
        """Obtiene todos los tipos de alarma de una empresa sin paginación"""
        try:
            if not ObjectId.is_valid(empresa_id):
                return {'success': False, 'error': 'ID de empresa inválido'}

            if not self.tipo_alarma_repo.verify_empresa_exists(empresa_id):
                return {'success': False, 'error': 'La empresa no existe'}

            tipos_alarma = self.tipo_alarma_repo.get_tipos_alarma_by_empresa_all(empresa_id, only_active=solo_activos)

            return {
                'success': True,
                'data': [tipo.to_json() for tipo in tipos_alarma],
                'count': len(tipos_alarma)
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
                color_alerta_value = update_data['color_alerta']
                if isinstance(color_alerta_value, str):
                    color_alerta_value = color_alerta_value.strip().upper()
                tipo_alarma.color_alerta = color_alerta_value

            if 'imagen_base64' in update_data:
                imagen_base64 = update_data['imagen_base64']
                if imagen_base64:
                    validation_result = self._validate_image_value(imagen_base64)
                    if not validation_result['valid']:
                        return {'success': False, 'error': validation_result['error']}
                tipo_alarma.imagen_base64 = imagen_base64

            if 'sonido_link' in update_data:
                tipo_alarma.sonido_link = update_data['sonido_link']

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
    
    def _validate_image_value(self, image_value):
        """
        Valida la cadena de imagen recibida

        Args:
            image_value (str): Cadena con referencia a imagen

        Returns:
            dict: Resultado de la validación
        """
        try:
            if not isinstance(image_value, str):
                return {'valid': False, 'error': 'La imagen debe ser una cadena de texto'}

            trimmed = image_value.strip()
            if len(trimmed) == 0:
                return {'valid': False, 'error': 'La imagen no puede estar vacía'}

            if len(trimmed) > 2048:
                return {'valid': False, 'error': 'La imagen no puede exceder 2048 caracteres'}

            return {'valid': True}

        except Exception as e:
            return {'valid': False, 'error': f'Error validando imagen: {str(e)}'}
