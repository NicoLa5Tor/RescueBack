from datetime import datetime
from bson import ObjectId

class MqttAlert:
    """Modelo para almacenar alertas recibidas por MQTT o creadas por usuarios"""
    
    def __init__(self, empresa_nombre=None, sede=None, data=None, 
                 # Campos para origen
                 origen_tipo=None,  # 'hardware' o 'usuario'
                 origen_id=None,    # hardware_id o usuario_id
                 # Campos específicos para alertas de usuario
                 usuario_id=None,
                 usuario_nombre=None,
                 tipo_alerta=None,
                 descripcion=None,
                 prioridad=None,
                 # Campos específicos para hardware (existentes)
                 hardware_nombre=None, 
                 hardware_id=None, 
                 numeros_telefonicos=None, 
                 topic=None, 
                 topics_otros_hardware=None, 
                 fecha_desactivacion=None, 
                 activo=True, 
                 _id=None):
        self._id = _id or ObjectId()
        self.empresa_nombre = empresa_nombre
        self.sede = sede
        self.data = data or {}  # datos de la alerta
        
        # Campos de origen
        self.origen_tipo = origen_tipo or 'hardware'  # por defecto hardware para compatibilidad
        self.origen_id = ObjectId(origen_id) if origen_id else None
        
        # Campos específicos para usuario
        self.usuario_id = ObjectId(usuario_id) if usuario_id else None
        self.tipo_alerta = tipo_alerta
        self.descripcion = descripcion
        self.prioridad = prioridad or 'media'
        
        # Campos específicos para hardware (existentes)
        self.hardware_nombre = hardware_nombre  # nombre del hardware que envió la alerta
        self.hardware_id = ObjectId(hardware_id) if hardware_id else None  # ID del hardware que envió la alerta
        self.numeros_telefonicos = numeros_telefonicos or []  # números telefónicos de usuarios relacionados
        self.topic = topic  # topic del hardware
        self.topics_otros_hardware = topics_otros_hardware or []  # topics de otros hardware de la misma empresa y sede
        
        # Campos comunes
        self.activo = activo  # estado activo/inactivo de la alerta
        self.fecha_creacion = datetime.utcnow()
        self.fecha_actualizacion = datetime.utcnow()
        self.fecha_desactivacion = fecha_desactivacion  # cuando se desactivó la alerta
        self.desactivado_por = {}  # información sobre quién/qué desactivó la alerta
        
        # Sincronizar origen_id con hardware_id o usuario_id
        if not self.origen_id:
            if self.origen_tipo == 'hardware' and self.hardware_id:
                self.origen_id = self.hardware_id
            elif self.origen_tipo == 'usuario' and self.usuario_id:
                self.origen_id = self.usuario_id
        
    def to_dict(self):
        """Convierte el objeto a diccionario para MongoDB"""
        alert_dict = {
            'empresa_nombre': self.empresa_nombre,
            'sede': self.sede,
            'data': self.data,
            'origen_tipo': self.origen_tipo,
            'origen_id': self.origen_id,
            'usuario_id': self.usuario_id,
            'tipo_alerta': self.tipo_alerta,
            'descripcion': self.descripcion,
            'prioridad': self.prioridad,
            'hardware_nombre': self.hardware_nombre,
            'hardware_id': self.hardware_id,
            'numeros_telefonicos': self.numeros_telefonicos,
            'topic': self.topic,
            'topics_otros_hardware': self.topics_otros_hardware,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion,
            'fecha_actualizacion': self.fecha_actualizacion,
            'fecha_desactivacion': self.fecha_desactivacion,
            'desactivado_por': self.desactivado_por
        }
        if self._id:
            alert_dict['_id'] = self._id
        return alert_dict
    
    @classmethod
    def from_dict(cls, data):
        """Crea un objeto MqttAlert desde un diccionario de MongoDB"""
        alert = cls()
        alert._id = data.get('_id')
        alert.empresa_nombre = data.get('empresa_nombre')
        alert.sede = data.get('sede')
        alert.data = data.get('data', {})
        alert.origen_tipo = data.get('origen_tipo', 'hardware')
        alert.origen_id = data.get('origen_id')
        alert.usuario_id = data.get('usuario_id')
        alert.tipo_alerta = data.get('tipo_alerta')
        alert.descripcion = data.get('descripcion')
        alert.prioridad = data.get('prioridad', 'media')
        alert.hardware_nombre = data.get('hardware_nombre')
        alert.hardware_id = data.get('hardware_id')
        alert.numeros_telefonicos = data.get('numeros_telefonicos', [])
        alert.topic = data.get('topic')
        alert.topics_otros_hardware = data.get('topics_otros_hardware', [])
        alert.activo = data.get('activo', True)
        alert.fecha_creacion = data.get('fecha_creacion')
        alert.fecha_actualizacion = data.get('fecha_actualizacion')
        alert.fecha_desactivacion = data.get('fecha_desactivacion')
        alert.desactivado_por = data.get('desactivado_por', {})
        return alert
    
    def to_json(self):
        """Convierte a JSON serializable"""
        return {
            '_id': str(self._id) if self._id else None,
            'empresa_nombre': self.empresa_nombre,
            'sede': self.sede,
            'data': self.data,
            'origen_tipo': self.origen_tipo,
            'origen_id': str(self.origen_id) if self.origen_id else None,
            'usuario_id': str(self.usuario_id) if self.usuario_id else None,
            'tipo_alerta': self.tipo_alerta,
            'descripcion': self.descripcion,
            'prioridad': self.prioridad,
            'hardware_nombre': self.hardware_nombre,
            'hardware_id': str(self.hardware_id) if self.hardware_id else None,
            'numeros_telefonicos': self.numeros_telefonicos,
            'topic': self.topic,
            'topics_otros_hardware': self.topics_otros_hardware,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'fecha_desactivacion': self.fecha_desactivacion.isoformat() if self.fecha_desactivacion else None,
            'desactivado_por': self.desactivado_por
        }
    
    def deactivate(self, desactivado_por_id=None, desactivado_por_tipo=None):
        """Desactiva la alerta"""
        self.activo = False
        self.fecha_desactivacion = datetime.utcnow()
        
        # Agregar información sobre quién desactivó
        if desactivado_por_id and desactivado_por_tipo:
            self.desactivado_por = {
                'id': desactivado_por_id,
                'tipo': desactivado_por_tipo,
                'fecha_desactivacion': self.fecha_desactivacion.isoformat()
            }
        
        self.update_timestamp()
    
    def activate(self):
        """Activa la alerta"""
        self.activo = True
        self.fecha_desactivacion = None
        self.update_timestamp()
    
    def toggle_status(self):
        """Alterna el estado activo/inactivo"""
        if self.activo:
            self.deactivate()
        else:
            self.activate()
    
    def update_timestamp(self):
        """Actualiza el timestamp de modificación"""
        self.fecha_actualizacion = datetime.utcnow()
    
    def validate(self):
        """Valida los datos de la alerta"""
        errors = []
        
        if not self.empresa_nombre or len(self.empresa_nombre.strip()) == 0:
            errors.append("El nombre de la empresa es obligatorio")
        
        if not self.sede or len(self.sede.strip()) == 0:
            errors.append("La sede es obligatoria")
        
        return errors
    
    def normalize_data(self):
        """Normaliza los datos antes de guardar"""
        if self.empresa_nombre:
            self.empresa_nombre = self.empresa_nombre.strip()
        if self.sede:
            self.sede = self.sede.strip()
    
    @classmethod
    def create_from_hardware(cls, empresa_nombre, sede, hardware_nombre, hardware_id, 
                           tipo_alerta=None, data=None, **kwargs):
        """Crea una alerta desde hardware MQTT"""
        return cls(
            empresa_nombre=empresa_nombre,
            sede=sede,
            origen_tipo='hardware',
            origen_id=hardware_id,
            hardware_nombre=hardware_nombre,
            hardware_id=hardware_id,
            tipo_alerta=tipo_alerta,
            data=data,
            **kwargs
        )
    
    @classmethod
    def create_from_user(cls, empresa_nombre, sede, usuario_id, tipo_alerta, 
                        descripcion, prioridad='media', data=None, **kwargs):
        """Crea una alerta desde usuario"""
        return cls(
            empresa_nombre=empresa_nombre,
            sede=sede,
            origen_tipo='usuario',
            origen_id=usuario_id,
            usuario_id=usuario_id,
            tipo_alerta=tipo_alerta,
            descripcion=descripcion,
            prioridad=prioridad,
            data=data,
            **kwargs
        )
