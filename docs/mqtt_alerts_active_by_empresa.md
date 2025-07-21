# Endpoint: Alertas Activas por Empresa y Sede

## Descripción
Este endpoint permite obtener las alertas activas filtradas por empresa y sede con paginación.

## URL
```
GET /proxy/api/mqtt-alerts/empresa/{empresaId}/active-by-sede
```

## Autenticación
- **Requerida**: Sí
- **Tipo**: Token de empresa
- **Decorador**: `@require_empresa_token`

## Parámetros

### URL Parameters
- `empresaId` (string, requerido): ID de la empresa en formato ObjectId de MongoDB

### Query Parameters
- `limit` (integer, opcional): Número de alertas por página (default: 5)
- `offset` (integer, opcional): Desplazamiento para paginación (default: 0)

### Ejemplo de URL
```
GET /proxy/api/mqtt-alerts/empresa/64f5a1b2c3d4e5f6789abcde/active-by-sede?limit=5&offset=0
```

## Respuesta

### Respuesta Exitosa (200)
```json
{
  "success": true,
  "data": [
    {
      "_id": "alert_id_123",
      "hardware_nombre": "Sensor Principal",
      "prioridad": "media",
      "activo": true,
      "empresa_nombre": "Nicolas Empresa",
      "sede": "Secundaria", 
      "fecha_creacion": "2024-07-21T10:30:00Z",
      "contactos_count": 2
    }
  ],
  "pagination": {
    "total_pages": 3,
    "current_page": 1,
    "total_items": 15,
    "has_next": true,
    "has_prev": false
  }
}
```

### Respuesta de Error de Autenticación (401)
```json
{
  "success": false,
  "errors": ["Token de autenticación requerido"]
}
```

### Respuesta de Error de Permisos (401)
```json
{
  "success": false,
  "errors": ["Permiso de empresa requerido"]
}
```

### Respuesta de Error de Parámetros (400)
```json
{
  "success": false,
  "error": "Parámetros de paginación inválidos",
  "message": "invalid literal for int() with base 10: 'abc'"
}
```

### Respuesta de Error del Servidor (500)
```json
{
  "success": false,
  "error": "Error interno del servidor",
  "message": "Database connection failed"
}
```

## Campos de la Respuesta

### Objeto Alert en data[]
- `_id`: ID único de la alerta
- `hardware_nombre`: Nombre del hardware que generó la alerta
- `prioridad`: Nivel de prioridad (baja, media, alta, critica)
- `activo`: Booleano que indica si la alerta está activa
- `empresa_nombre`: Nombre de la empresa
- `sede`: Nombre de la sede donde ocurrió la alerta
- `fecha_creacion`: Timestamp ISO 8601 de creación
- `contactos_count`: Número de contactos relacionados a la alerta

### Objeto Pagination
- `total_pages`: Número total de páginas disponibles
- `current_page`: Página actual (calculada desde offset)
- `total_items`: Número total de elementos
- `has_next`: Booleano indicando si hay página siguiente
- `has_prev`: Booleano indicando si hay página anterior

## Implementación

### Repositorio
- **Archivo**: `repositories/mqtt_alert_repository.py`
- **Método**: `get_active_alerts_by_empresa_sede(empresa_id, page=1, limit=5)`
- **Query MongoDB**: `{'empresa_id': ObjectId(empresa_id), 'estado_activo': True}`

### Servicio
- **Archivo**: `services/mqtt_alert_service.py`  
- **Método**: `get_alerts_active_by_empresa_sede(empresa_id, page=1, limit=5)`

### Controlador
- **Archivo**: `controllers/mqtt_alert_controller.py`
- **Método**: `get_active_alerts_by_empresa_sede(empresa_id)`

### Ruta
- **Archivo**: `routes.py`
- **Función**: `get_active_alerts_by_empresa_sede(empresa_id)`

## Notas Técnicas

1. **Paginación**: El endpoint convierte automáticamente el parámetro `offset` a página interna usando la fórmula `page = (offset // limit) + 1`

2. **Autenticación**: Solo usuarios con token de empresa pueden acceder a este endpoint

3. **Filtrado**: Las alertas se filtran por:
   - `empresa_id`: ID de la empresa (ObjectId)
   - `estado_activo: true`: Solo alertas activas

4. **Ordenamiento**: Las alertas se ordenan por `fecha_creacion` descendente (más recientes primero)

5. **Transformación de Datos**: Los datos se transforman para coincidir exactamente con el formato solicitado, incluyendo el conteo de contactos extraído del campo `data.numeros_telefonicos`

## Casos de Uso

- Dashboards de empresa para mostrar alertas activas paginadas
- APIs móviles que necesitan cargar alertas de forma incremental
- Sistemas de notificación que procesan alertas por lotes

## Seguridad

- Autenticación obligatoria con token de empresa
- Filtrado automático por empresa para prevenir acceso a datos de otras empresas
- Validación de parámetros de entrada para prevenir inyecciones
