# Endpoint: Crear Alertas por Usuario

## Descripción
Este endpoint permite crear alertas tanto por usuarios individuales como por empresas. **No requiere autenticación**.

## URL
```
POST /api/mqtt-alerts/user-alert
```

## Autenticación
- **Sin autenticación requerida**

## Cuerpo de la Petición (JSON)

### Estructura para Usuario
```json
{
  "creador": {
    "usuario_id": "string",        // ID del usuario (OBLIGATORIO)
    "tipo": "usuario"              // Tipo de creador (opcional, por defecto "usuario")
  },
  "ubicacion": {                   // OPCIONAL para usuarios
    "latitud": "string",           // Coordenada de latitud
    "longitud": "string"           // Coordenada de longitud
  },
  "tipo_alerta": "string",         // Tipo de alerta (OBLIGATORIO)
  "descripcion": "string",         // Descripción de la alerta (OBLIGATORIO)
  "prioridad": "string"            // Prioridad: "baja", "media", "alta" (opcional, por defecto "media")
}
```

### Estructura para Empresa
```json
{
  "creador": {
    "empresa_id": "string",        // ID de la empresa (OBLIGATORIO)
    "tipo": "empresa",             // Tipo de creador (OBLIGATORIO)
    "sede": "string"               // Sede de la empresa (OBLIGATORIO)
  },
  "tipo_alerta": "string",         // Tipo de alerta (OBLIGATORIO)
  "descripcion": "string",         // Descripción de la alerta (OBLIGATORIO)
  "prioridad": "string"            // Prioridad: "baja", "media", "alta" (opcional, por defecto "media")
}
```

## Cambios Implementados

### 1. Ubicación Opcional para Usuarios
- **Antes**: La ubicación era obligatoria para todos los usuarios
- **Ahora**: La ubicación es opcional para usuarios individuales
- Si un usuario proporciona ubicación, debe incluir tanto `latitud` como `longitud`

### 2. Soporte para Empresas como Creadoras
- **Nuevo**: Las empresas pueden crear alertas especificando la sede
- **Validaciones**:
  - Verifica que la empresa exista en la base de datos
  - Verifica que la sede tenga una botonera activa
  - Usa automáticamente la ubicación de la botonera de esa sede

### 3. Ubicación Automática para Empresas
- Cuando una empresa crea una alerta, el sistema:
  1. Busca la botonera activa en la sede especificada
  2. Usa las coordenadas de la botonera (o valores por defecto si no las tiene)
  3. Usa la dirección de la botonera para los mapas

## Ejemplos de Uso

### Ejemplo 1: Usuario con Ubicación
```bash
curl -X POST http://localhost:5000/api/mqtt-alerts/user-alert \
  -H "Content-Type: application/json" \
  -d '{
    "creador": {
      "usuario_id": "64a1b2c3d4e5f6789012346",
      "tipo": "usuario"
    },
    "ubicacion": {
      "latitud": "4.6097",
      "longitud": "-74.0817"
    },
    "tipo_alerta": "emergencia",
    "descripcion": "Emergencia médica en edificio principal",
    "prioridad": "alta"
  }'
```

### Ejemplo 2: Usuario sin Ubicación
```bash
curl -X POST http://localhost:5000/api/mqtt-alerts/user-alert \
  -H "Content-Type: application/json" \
  -d '{
    "creador": {
      "usuario_id": "64a1b2c3d4e5f6789012346",
      "tipo": "usuario"
    },
    "tipo_alerta": "incidente",
    "descripcion": "Reporte de incidente de seguridad"
  }'
```

### Ejemplo 3: Empresa Creando Alerta
```bash
curl -X POST http://localhost:5000/api/mqtt-alerts/user-alert \
  -H "Content-Type: application/json" \
  -d '{
    "creador": {
      "empresa_id": "64a1b2c3d4e5f6789012350",
      "tipo": "empresa",
      "sede": "Principal"
    },
    "tipo_alerta": "evacuacion",
    "descripcion": "Simulacro de evacuación programado",
    "prioridad": "media"
  }'
```

## Validaciones

### Para Usuarios (`tipo: "usuario"`)
1. **Campo `usuario_id`**: Obligatorio, debe existir en la base de datos
2. **Campo `ubicacion`**: Opcional
   - Si se proporciona, debe incluir `latitud` y `longitud`
   - Ambas coordenadas deben ser strings no vacías

### Para Empresas (`tipo: "empresa"`)
1. **Campo `empresa_id`**: Obligatorio, debe existir en la base de datos
2. **Campo `sede`**: Obligatorio, debe tener una botonera activa
3. **Campo `ubicacion`**: No se acepta (se usa la de la botonera)

### Validaciones Comunes
1. **`tipo_alerta`**: Obligatorio, string no vacío
2. **`descripcion`**: Obligatorio, string no vacío
3. **`prioridad`**: Opcional, valores válidos: "baja", "media", "alta"
4. **`tipo` en creador**: Valores válidos: "usuario", "empresa"

## Procesamiento Interno

### Para Usuarios
1. Busca el usuario en la base de datos
2. Obtiene la empresa asociada al usuario
3. Usa la sede del usuario (o "Principal" por defecto)
4. Si hay ubicación proporcionada, genera URLs de mapas
5. Busca la botonera de la empresa/sede para información adicional

### Para Empresas
1. Verifica que la empresa exista y sea legítima
2. Busca la botonera activa en la sede especificada
3. Usa automáticamente las coordenadas de la botonera
4. Usa la dirección de la botonera para generar URLs de mapas

### Procesamiento Común
1. Obtiene todos los usuarios de la empresa/sede para notificaciones
2. Busca información del tipo de alerta (imagen, elementos, instrucciones)
3. Genera topics de hardware para notificaciones MQTT
4. Crea y guarda la alerta en la base de datos

## Respuestas

### Éxito (201)
```json
{
  "success": true,
  "message": "Alerta de usuario creada exitosamente",
  "alert": {
    // Objeto completo de la alerta creada
  }
}
```

### Errores Comunes

#### Usuario no encontrado (404)
```json
{
  "success": false,
  "error": "Usuario no encontrado",
  "message": "No existe un usuario con el ID {usuario_id}"
}
```

#### Empresa no encontrada (404)
```json
{
  "success": false,
  "error": "Empresa no encontrada",
  "message": "No existe una empresa con el ID {empresa_id}"
}
```

#### Botonera no encontrada para empresa (404)
```json
{
  "success": false,
  "error": "Botonera no encontrada",
  "message": "No se encontró una botonera activa en la sede \"Principal\" de la empresa \"Mi Empresa\""
}
```

#### Campos requeridos faltantes (400)
```json
{
  "success": false,
  "error": "Campo creador requerido",
  "message": "El campo \"creador\" es obligatorio",
  "estructura_esperada": {
    "usuario": {"creador": {"usuario_id": "string", "tipo": "usuario"}, "ubicacion": {"latitud": "string", "longitud": "string"}},
    "empresa": {"creador": {"empresa_id": "string", "tipo": "empresa", "sede": "string"}}
  }
}
```

## Notas Importantes

1. **Ubicación Opcional**: Los usuarios ya no están obligados a proporcionar ubicación
2. **Empresas Usan Botoneras**: Las empresas utilizan automáticamente la ubicación de su botonera
3. **Validación de Empresas**: Se verifica que la empresa existe y tiene botonera en la sede
4. **Sin Autenticación**: El endpoint permanece sin autenticación para facilitar el acceso desde apps móviles
5. **Flexibilidad**: Soporta tanto usuarios individuales como empresas como creadoras
6. **Coordenadas por Defecto**: Si una botonera no tiene coordenadas, se usan valores por defecto (0.0, 0.0)

## Códigos de Estado HTTP
- `201`: Alerta creada exitosamente
- `400`: Error en la petición (formato inválido, campos requeridos faltantes)
- `404`: Usuario, empresa o botonera no encontrada
- `500`: Error interno del servidor
