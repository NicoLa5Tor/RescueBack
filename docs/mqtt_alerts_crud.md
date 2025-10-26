# CRUD de Alertas MQTT - Documentación

## Resumen
Este documento describe el CRUD completo de alertas MQTT implementado con restricciones de acceso basadas en tokens de hardware.

## Autenticación y Autorización

### Token de Hardware (REQUERIDO para POST)
- **Endpoint de autenticación**: `POST /api/hardware-auth/authenticate`
- **Solo el token obtenido del login de hardware** puede crear alertas
- Los endpoints que requieren token de hardware:
  - `POST /api/mqtt-alerts/process` - Procesar mensaje MQTT
  - `POST /api/mqtt-alerts` - Crear nueva alerta

### Token General (REQUERIDO para GET, PUT, DELETE)
- Los demás endpoints requieren autenticación general de empresa o admin
- Incluye lectura, actualización, eliminación y operaciones especiales

## Endpoints del CRUD

### 1. Crear Alerta (Solo Token de Hardware)
```http
POST /api/mqtt-alerts
Authorization: Bearer <token_de_hardware>
Content-Type: application/json

{
  "empresa_nombre": "string",
  "sede": "string",
  "tipo_alerta": "string",
  "hardware_nombre": "string",
  "datos_hardware": {},
  "mensaje_original": "string",
  "data": {}
}
```

**Nota**: El campo `hardware_id` se extrae automáticamente del token de hardware y se asigna a la alerta.

### 2. Procesar Mensaje MQTT (Solo Token de Hardware)
```http
POST /api/mqtt-alerts/process
Authorization: Bearer <token_de_hardware>
Content-Type: application/json

{
  // Estructura de mensaje MQTT
}
```

### 3. Leer Alertas
```http
GET /api/mqtt-alerts?page=1&limit=50
Authorization: Bearer <token_general>
```

### 4. Leer Alerta por ID
```http
GET /api/mqtt-alerts/{alert_id}
Authorization: Bearer <token_general>
```

### 5. Actualizar Alerta
```http
PUT /api/mqtt-alerts/{alert_id}
Authorization: Bearer <token_general>
Content-Type: application/json

{
  "empresa_nombre": "string",
  "sede": "string",
  // otros campos a actualizar
}
```

### 6. Eliminar Alerta
```http
DELETE /api/mqtt-alerts/{alert_id}
Authorization: Bearer <token_general>
```

### 7. Autorizar Alerta
```http
PATCH /api/mqtt-alerts/{alert_id}/authorize
Authorization: Bearer <token_general>
Content-Type: application/json

{
  "usuario_id": "string"
}
```

### 8. Alternar Estado de Alerta
```http
PATCH /api/mqtt-alerts/{alert_id}/toggle-status
Authorization: Bearer <token_general>
```

## Endpoints de Consulta Específica

### Alertas por Empresa
```http
GET /api/mqtt-alerts/empresa/{empresa_id}?page=1&limit=50
Authorization: Bearer <token_general>
```

### Alertas Activas
```http
GET /api/mqtt-alerts/active?page=1&limit=50
Authorization: Bearer <token_general>
```

### Alertas No Autorizadas
```http
GET /api/mqtt-alerts/unauthorized?page=1&limit=50
Authorization: Bearer <token_general>
```

### Estadísticas de Alertas
```http
GET /api/mqtt-alerts/stats
Authorization: Bearer <token_general>
```

## Endpoints de Utilidad

### Verificar Empresa y Sede
```http
GET /api/mqtt-alerts/verify-empresa-sede?empresa_nombre=X&sede=Y
Authorization: Bearer <token_general>
```

### Verificar Hardware
```http
GET /api/mqtt-alerts/verify-hardware?hardware_nombre=X
Authorization: Bearer <token_general>
```

### Probar Flujo (Público)
```http
GET /api/mqtt-alerts/test-flow
```

## Estructura de Datos

### Modelo de Alerta
```json
{
  "_id": "ObjectId",
  "empresa_nombre": "string",
  "sede": "string",
  "tipo_alerta": "string",
  "datos_hardware": {},
  "mensaje_original": "string",
  "autorizado": false,
  "estado_activo": true,
  "usuario_autorizador": "ObjectId",
  "fecha_autorizacion": "datetime",
  "usuarios_notificados": [],
  "data": {},
  "hardware_nombre": "string",
  "fecha_creacion": "datetime",
  "fecha_actualizacion": "datetime"
}
```

### Campos Requeridos para Crear Alerta
- `empresa_nombre`: Nombre de la empresa
- `sede`: Nombre de la sede
- `tipo_alerta`: Tipo de alerta (ej: "semaforo", "alarma", "emergencia")
- `hardware_nombre`: Nombre del hardware que genera la alerta

### Campos Automáticos (del Token)
- `hardware_id`: Se extrae del token de hardware (ObjectId) y referencia al hardware específico

## Códigos de Respuesta

- `200`: Operación exitosa
- `201`: Alerta creada exitosamente
- `400`: Datos inválidos o campos requeridos faltantes
- `401`: Token de autenticación requerido o inválido
- `404`: Alerta no encontrada
- `500`: Error interno del servidor

## Seguridad

### Restricciones de Acceso
1. **POST endpoints**: Solo accesibles con token de hardware válido
2. **GET/PUT/DELETE endpoints**: Requieren token general de empresa o admin
3. **Validación de tokens**: Los tokens se verifican en cada request
4. **Expiración**: Los tokens de hardware tienen duración limitada (5 minutos por defecto)

### Validaciones
- Verificación de existencia de hardware
- Validación de estructura de datos
- Normalización de datos antes de guardar
- Verificación de empresa y sede asociadas

## Tipos de Alarma Globales

- Los tipos de alarma sin `empresa_id` se tratan como **globales** y se incluyen por defecto en los listados (`GET /api/tipos-alarma/*`).
- Todos los endpoints de lectura aceptan el query param opcional `excluir_globales=true` para obtener exclusivamente tipos asociados a empresas.

## Ejemplo de Uso Completo

### 1. Obtener Token de Hardware
```bash
curl -X POST http://localhost:5000/api/hardware-auth/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "empresa_nombre": "MiEmpresa",
    "sede_nombre": "Sede1", 
    "hardware_nombre": "sensor01"
  }'
```

### 2. Crear Alerta con Token de Hardware
```bash
curl -X POST http://localhost:5000/api/mqtt-alerts \
  -H "Authorization: Bearer <token_de_hardware>" \
  -H "Content-Type: application/json" \
  -d '{
    "empresa_nombre": "MiEmpresa",
    "sede": "Sede1",
    "tipo_alerta": "emergencia",
    "hardware_nombre": "sensor01",
    "datos_hardware": {"temperatura": 85, "humedad": 60},
    "mensaje_original": "Temperatura crítica detectada"
  }'
```

**Nota**: El campo `hardware_id` se toma automáticamente del token y se asigna a la alerta para referenciar al hardware específico.

### 3. Leer Alertas con Token General
```bash
curl -X GET http://localhost:5000/api/mqtt-alerts \
  -H "Authorization: Bearer <token_general>"
```

## Notas Importantes

1. **Solo el token de hardware puede crear alertas** - Esta es la restricción principal solicitada
2. **El hardware_id se extrae automáticamente del token** - No es necesario proporcionarlo manualmente
3. **El token de hardware incluye el hardware_id** - Referencia directa al hardware que se autentica
4. **Los tokens de hardware son de corta duración** - Se deben renovar frecuentemente (5 minutos por defecto)
5. **Validación automática** - El sistema verifica la existencia de hardware, empresa y sede
6. **Referencia directa al hardware** - Cada alerta tiene una referencia por ObjectId al hardware específico
7. **Paginación** - Todos los endpoints de listado soportan paginación
8. **Logging** - Todas las operaciones se registran para auditoría

## Estados de Alerta

- `autorizado`: `false` por defecto, `true` cuando se autoriza
- `estado_activo`: `true` por defecto, se puede alternar
- `usuarios_notificados`: Lista de usuarios que han sido notificados
- `fecha_autorizacion`: Se establece cuando se autoriza la alerta
