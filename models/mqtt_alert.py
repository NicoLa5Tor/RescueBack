from datetime import datetime
from bson import ObjectId

class MqttAlert:
    """Modelo para almacenar alertas recibidas por MQTT"""
    
    def __init__(self, empresa_nombre=None, sede=None, tipo_alerta=None, 
                 datos_hardware=None, mensaje_original=None, autorizado=False, 
                 estado_activo=True, usuario_autorizador=None, fecha_autorizacion=None,
                 usuarios_notificados=None, data=None, hardware_nombre=None, _id=None):
        self._id = _id or ObjectId()
        self.empresa_nombre = empresa_nombre
        self.sede = sede
        self.tipo_alerta = tipo_alerta  # semaforo, alarma, etc.
        self.datos_hardware = datos_hardware or {}  # datos del hardware que envió la alerta
        self.mensaje_original = mensaje_original  # mensaje MQTT original
        self.autorizado = autorizado  # False por defecto, True cuando se autorice
        self.estado_activo = estado_activo  # True = alerta activa, False = alerta desactivada
        self.usuario_autorizador = usuario_autorizador  # ID del usuario que autorizó
        self.fecha_autorizacion = fecha_autorizacion  # cuando se autorizó
        self.usuarios_notificados = usuarios_notificados or []  # lista de usuarios notificados
        self.data = data or {}  # datos adicionales como rutas, metadatos, etc.
        self.hardware_nombre = hardware_nombre  # nombre del hardware que envió la alerta
        self.fecha_creacion = datetime.utcnow()
        self.fecha_actualizacion = datetime.utcnow()
        
    def to_dict(self):
        """Convierte el objeto a diccionario para MongoDB"""
        alert_dict = {
            'empresa_nombre': self.empresa_nombre,
            'sede': self.sede,
            'tipo_alerta': self.tipo_alerta,
            'datos_hardware': self.datos_hardware,
            'mensaje_original': self.mensaje_original,
            'autorizado': self.autorizado,
            'estado_activo': self.estado_activo,
            'usuario_autorizador': self.usuario_autorizador,
            'fecha_autorizacion': self.fecha_autorizacion,
            'usuarios_notificados': self.usuarios_notificados,
            'data': self.data,
            'hardware_nombre': self.hardware_nombre,
            'fecha_creacion': self.fecha_creacion,
            'fecha_actualizacion': self.fecha_actualizacion
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
        alert.tipo_alerta = data.get('tipo_alerta')
        alert.datos_hardware = data.get('datos_hardware', {})
        alert.mensaje_original = data.get('mensaje_original')
        alert.autorizado = data.get('autorizado', False)
        alert.estado_activo = data.get('estado_activo', True)
        alert.usuario_autorizador = data.get('usuario_autorizador')
        alert.fecha_autorizacion = data.get('fecha_autorizacion')
        alert.usuarios_notificados = data.get('usuarios_notificados', [])
        alert.data = data.get('data', {})
        alert.hardware_nombre = data.get('hardware_nombre')
        alert.fecha_creacion = data.get('fecha_creacion')
        alert.fecha_actualizacion = data.get('fecha_actualizacion')
        return alert
    
    def to_json(self):
        """Convierte a JSON serializable"""
        return {
            '_id': str(self._id) if self._id else None,
            'empresa_nombre': self.empresa_nombre,
            'sede': self.sede,
            'tipo_alerta': self.tipo_alerta,
            'datos_hardware': self.datos_hardware,
            'mensaje_original': self.mensaje_original,
            'autorizado': self.autorizado,
            'estado_activo': self.estado_activo,
            'usuario_autorizador': str(self.usuario_autorizador) if self.usuario_autorizador else None,
            'fecha_autorizacion': self.fecha_autorizacion.isoformat() if self.fecha_autorizacion else None,
            'usuarios_notificados': self.usuarios_notificados,
            'data': self.data,
            'hardware_nombre': self.hardware_nombre,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }
    
    def authorize(self, usuario_id):
        """Autoriza la alerta"""
        self.autorizado = True
        self.usuario_autorizador = ObjectId(usuario_id) if usuario_id else None
        self.fecha_autorizacion = datetime.utcnow()
        self.update_timestamp()
    
    def deactivate(self):
        """Desactiva la alerta"""
        self.estado_activo = False
        self.update_timestamp()
    
    def activate(self):
        """Activa la alerta"""
        self.estado_activo = True
        self.update_timestamp()
    
    def add_notified_user(self, usuario_info):
        """Agrega un usuario notificado"""
        if usuario_info not in self.usuarios_notificados:
            self.usuarios_notificados.append(usuario_info)
            self.update_timestamp()
    
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
        
        if not self.tipo_alerta or len(self.tipo_alerta.strip()) == 0:
            errors.append("El tipo de alerta es obligatorio")
        
        if not self.mensaje_original:
            errors.append("El mensaje original es obligatorio")
        
        return errors
    
    def normalize_data(self):
        """Normaliza los datos antes de guardar"""
        if self.empresa_nombre:
            self.empresa_nombre = self.empresa_nombre.strip()
        if self.sede:
            self.sede = self.sede.strip()
        if self.tipo_alerta:
            self.tipo_alerta = self.tipo_alerta.strip().lower()
