# Endpoint: Actualizar Estado de Usuario en Alerta

## Descripción
Este endpoint permite actualizar el estado de un usuario específico dentro de la lista de números telefónicos de una alerta. Solo permite modificar las llaves `disponible` y `embarcado`.

## URL
```
PATCH /api/mqtt-alerts/{alert_id}/usuarios/{usuario_id}
```

## Autenticación
- Requiere token de empresa o admin (`@require_empresa_or_admin_token`)

## Parámetros de URL
- `alert_id` (string): ID de la alerta que se desea modificar
- `usuario_id` (string): ID del usuario cuyo estado se desea actualizar

## Cuerpo de la Petición (JSON)
```json
{
  "disponible": true,
  "embarcado": false
}
```

### Campos Permitidos
- `disponible` (boolean): Indica si el usuario está disponible
- `embarcado` (boolean): Indica si el usuario está embarcado

**Nota**: Solo se pueden actualizar estos dos campos. Si se envían otros campos, serán ignorados.

## Respuestas

### Éxito (200)
```json
{
  "success": true,
  "alert": {
    "_id": "64a1b2c3d4e5f6789012345",
    "empresa_nombre": "Mi Empresa",
    "sede": "Principal",
    "numeros_telefonicos": [
      {
        "numero": "+573001234567",
        "nombre": "Juan Pérez",
        "usuario_id": "64a1b2c3d4e5f6789012346",
        "disponible": true,
        "embarcado": false
      }
    ],
    "activo": true,
    "fecha_creacion": "2024-01-15T10:30:00.000Z",
    "fecha_actualizacion": "2024-01-15T11:45:00.000Z"
  }
}
```

### Error - Alerta no encontrada (404)
```json
{
  "success": false,
  "error": "Alert not found"
}
```

### Error - Usuario no encontrado en la alerta (404)
```json
{
  "success": false,
  "error": "User not found in this alert"
}
```

### Error - Formato inválido (400)
```json
{
  "success": false,
  "error": "Invalid format",
  "message": "Content must be JSON"
}
```

### Error - Campos no válidos (400)
```json
{
  "success": false,
  "error": "No valid fields to update"
}
```

### Error - Sin cambios (400)
```json
{
  "success": false,
  "error": "No changes were made"
}
```

## Ejemplos de Uso

### Ejemplo 1: Marcar usuario como disponible
```bash
curl -X PATCH \
  'http://localhost:5000/api/mqtt-alerts/64a1b2c3d4e5f6789012345/usuarios/64a1b2c3d4e5f6789012346' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer tu-token-aqui' \
  -d '{
    "disponible": true
  }'
```

### Ejemplo 2: Marcar usuario como embarcado y no disponible
```bash
curl -X PATCH \
  'http://localhost:5000/api/mqtt-alerts/64a1b2c3d4e5f6789012345/usuarios/64a1b2c3d4e5f6789012346' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer tu-token-aqui' \
  -d '{
    "disponible": false,
    "embarcado": true
  }'
```

### Ejemplo 3: Intentar actualizar campo no permitido (será ignorado)
```bash
curl -X PATCH \
  'http://localhost:5000/api/mqtt-alerts/64a1b2c3d4e5f6789012345/usuarios/64a1b2c3d4e5f6789012346' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer tu-token-aqui' \
  -d '{
    "disponible": true,
    "nombre": "Nuevo Nombre",
    "telefono": "+573009876543"
  }'
```
**Resultado**: Solo se actualizará `disponible`, los otros campos serán ignorados.

## Notas Importantes

1. **Validación de campos**: Solo se procesan los campos `disponible` y `embarcado`. Cualquier otro campo en el JSON será ignorado.

2. **Existencia de datos**: El endpoint verifica que:
   - La alerta exista
   - El usuario esté presente en la lista de números telefónicos de esa alerta

3. **Actualización atómica**: La operación utiliza MongoDB's `arrayFilters` para actualizar solo el elemento específico del array.

4. **Respuesta completa**: En caso de éxito, devuelve la alerta completa actualizada en formato JSON.

5. **Seguridad**: Requiere autenticación con token de empresa o admin.

## Códigos de Estado HTTP
- `200`: Actualización exitosa
- `400`: Error en la petición (formato inválido, campos no válidos, sin cambios)
- `404`: Alerta o usuario no encontrado
- `500`: Error interno del servidor

## Estructura de la Lista de Números Telefónicos
Cada elemento en `numeros_telefonicos` tiene la siguiente estructura:
```json
{
  "numero": "+573001234567",
  "nombre": "Juan Pérez",
  "usuario_id": "64a1b2c3d4e5f6789012346",
  "disponible": false,
  "embarcado": false
}
```

Donde solo `disponible` y `embarcado` pueden ser modificados mediante este endpoint.
