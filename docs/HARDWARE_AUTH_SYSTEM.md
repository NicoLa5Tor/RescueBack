# Sistema de Autenticación de Hardware

## Descripción General

El Sistema de Autenticación de Hardware es una solución unificada que valida la identidad del hardware, empresa y sede en un **único endpoint**, generando un token temporal JWT válido por 5 minutos para autorizar el envío de alertas MQTT.

## Características Principales

- ✅ **Endpoint único** para todo el proceso de autenticación
- ✅ **Validación completa** de hardware, empresa y sede
- ✅ **Tokens temporales JWT** con expiración de 5 minutos
- ✅ **Principios SOLID** aplicados en el diseño
- ✅ **Gestión de sesiones** activas
- ✅ **Limpieza automática** de sesiones expiradas

## Flujo de Autenticación

### 1. Proceso de Autenticación

```mermaid
graph TD
    A[Hardware solicita autenticación] --> B[Validar parámetros]
    B --> C[Verificar empresa existe y activa]
    C --> D[Verificar sede existe en empresa]
    D --> E[Verificar hardware existe, activo y pertenece a empresa]
    E --> F[Generar token JWT temporal]
    F --> G[Registrar sesión de autenticación]
    G --> H[Retornar token con expiración]
```

### 2. Uso del Token

```mermaid
graph TD
    I[Hardware recibe token] --> J[Incluir token en header Authorization]
    J --> K[Enviar mensaje MQTT]
    K --> L[Sistema verifica token]
    L --> M[Token válido?]
    M -->|Sí| N[Procesar mensaje]
    M -->|No| O[Rechazar mensaje]
```

## Endpoints Disponibles

### 1. Autenticación de Hardware

**Endpoint único que realiza todo el proceso de validación**

```http
POST /api/hardware-auth/authenticate
Content-Type: application/json

{
    "hardware_nombre": "Sensor001",
    "empresa_nombre": "TechCorp",
    "sede": "Sede Principal"
}
```

**Respuesta exitosa (200):**
```json
{
    "success": true,
    "message": "Autenticación exitosa",
    "data": {
        "hardware_id": "507f1f77bcf86cd799439011",
        "hardware_nombre": "Sensor001",
        "empresa_id": "507f1f77bcf86cd799439012",
        "empresa_nombre": "TechCorp",
        "sede": "Sede Principal",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "expires_at": "2024-01-15T15:30:00.000Z",
        "valid_for_minutes": 5
    }
}
```

**Respuesta de error (401):**
```json
{
    "success": false,
    "error": "Hardware no encontrado",
    "message": "El hardware \"Sensor001\" no existe, está inactivo o no pertenece a la empresa especificada"
}
```

### 2. Verificación de Token

```http
POST /api/hardware-auth/verify-token
Authorization: Bearer <token>
```

**Respuesta exitosa (200):**
```json
{
    "success": true,
    "payload": {
        "hardware_id": "507f1f77bcf86cd799439011",
        "hardware_nombre": "Sensor001",
        "empresa_id": "507f1f77bcf86cd799439012",
        "empresa_nombre": "TechCorp",
        "sede": "Sede Principal",
        "issued_at": 1642258800.0,
        "expires_at": 1642259100.0,
        "token_type": "hardware_auth"
    }
}
```

### 3. Sesiones Activas

```http
GET /api/hardware-auth/sessions?hardware_id=<hardware_id>
```

**Respuesta (200):**
```json
{
    "success": true,
    "data": [
        {
            "hardware_id": "507f1f77bcf86cd799439011",
            "hardware_nombre": "Sensor001",
            "empresa_id": "507f1f77bcf86cd799439012",
            "empresa_nombre": "TechCorp",
            "sede": "Sede Principal",
            "authenticated_at": "2024-01-15T15:25:00.000Z",
            "expires_at": "2024-01-15T15:30:00.000Z",
            "session_type": "hardware_auth"
        }
    ],
    "total": 1
}
```

### 4. Limpieza de Sesiones

```http
DELETE /api/hardware-auth/cleanup
```

**Respuesta (200):**
```json
{
    "success": true,
    "deleted_count": 3,
    "message": "Se eliminaron 3 sesiones expiradas"
}
```

### 5. Información del Sistema

```http
GET /api/hardware-auth/info
```

## Uso del Token para Envío de Alertas

Una vez obtenido el token, se debe incluir en el header Authorization para enviar mensajes MQTT:

```http
POST /api/mqtt-alerts/process
Authorization: Bearer <token>
Content-Type: application/json

{
    "empresa1": {
        "semaforo": {
            "sede": "principal",
            "alerta": "roja",
            "ubicacion": "Cruce principal",
            "hardware_id": "SEM001",
            "nombre": "Semaforo001",
            "coordenadas": {"lat": 4.6097, "lng": -74.0817}
        }
    }
}
```

## Estructura de Datos

### Token JWT Payload

```json
{
    "hardware_id": "507f1f77bcf86cd799439011",
    "hardware_nombre": "Sensor001",
    "empresa_id": "507f1f77bcf86cd799439012",
    "empresa_nombre": "TechCorp",
    "sede": "Sede Principal",
    "issued_at": 1642258800.0,
    "expires_at": 1642259100.0,
    "token_type": "hardware_auth"
}
```

### Sesión de Autenticación

```json
{
    "hardware_id": "ObjectId",
    "hardware_nombre": "string",
    "empresa_id": "ObjectId",
    "empresa_nombre": "string",
    "sede": "string",
    "authenticated_at": "datetime",
    "expires_at": "datetime",
    "session_type": "hardware_auth"
}
```

## Códigos de Error

| Código | Significado | Descripción |
|--------|-------------|-------------|
| 200 | OK | Operación exitosa |
| 400 | Bad Request | Parámetros faltantes o inválidos |
| 401 | Unauthorized | Autenticación fallida o token inválido |
| 500 | Internal Server Error | Error interno del servidor |

## Ejemplos de Uso

### Ejemplo 1: Autenticación Exitosa

```bash
curl -X POST http://localhost:5002/api/hardware-auth/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "hardware_nombre": "Sensor001",
    "empresa_nombre": "TechCorp",
    "sede": "Sede Principal"
  }'
```

### Ejemplo 2: Verificación de Token

```bash
curl -X POST http://localhost:5002/api/hardware-auth/verify-token \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Ejemplo 3: Envío de Mensaje MQTT

```bash
curl -X POST http://localhost:5002/api/mqtt-alerts/process \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "empresa1": {
      "semaforo": {
        "sede": "principal",
        "alerta": "roja",
        "ubicacion": "Cruce principal",
        "hardware_id": "SEM001",
        "nombre": "Semaforo001",
        "coordenadas": {"lat": 4.6097, "lng": -74.0817}
      }
    }
  }'
```

## Seguridad

### Características de Seguridad

1. **Tokens JWT con expiración**: 5 minutos máximo
2. **Validación completa**: Hardware, empresa y sede
3. **Sesiones registradas**: Auditoría de autenticaciones
4. **Limpieza automática**: Sesiones expiradas se pueden limpiar
5. **Validación de formato**: Tokens JWT bien formados

### Mejores Prácticas

1. **Renovar tokens**: Antes de los 5 minutos de expiración
2. **Manejar errores**: Implementar retry en caso de token expirado
3. **Almacenar temporalmente**: No persistir tokens en storage permanente
4. **Logs de auditoría**: Registrar intentos de autenticación

## Configuración

### Variables de Entorno (Recomendado para Producción)

```env
HARDWARE_AUTH_SECRET_KEY=your-secret-key-here
HARDWARE_AUTH_TOKEN_EXPIRY=5
```

### Configuración en Código

```python
class HardwareAuthService:
    def __init__(self):
        self.secret_key = os.getenv('HARDWARE_AUTH_SECRET_KEY', 'default-key')
        self.token_expiry_minutes = int(os.getenv('HARDWARE_AUTH_TOKEN_EXPIRY', '5'))
```

## Pruebas

### Ejecutar Pruebas Automáticas

```bash
cd /home/nicolas/Escritorio/ECOES/RescueBack
python test_hardware_auth.py
```

### Pruebas Manuales

1. **Servidor ejecutándose**: `python app.py`
2. **Puerto**: 5002
3. **Base de datos**: MongoDB corriendo
4. **Datos de prueba**: Empresas y hardware creados

## Arquitectura y Principios SOLID

### Single Responsibility Principle (SRP)
- `HardwareAuthService`: Solo maneja autenticación
- `HardwareAuthController`: Solo maneja endpoints HTTP
- `auth_utils`: Solo maneja utilidades de tokens

### Open/Closed Principle (OCP)
- Extensible para nuevos tipos de validación
- Nuevo tipos de tokens sin modificar código existente

### Liskov Substitution Principle (LSP)
- Interfaces consistentes
- Implementaciones intercambiables

### Interface Segregation Principle (ISP)
- Interfaces específicas por funcionalidad
- No forzar implementaciones no utilizadas

### Dependency Inversion Principle (DIP)
- Dependencias a abstracciones (Database)
- Inversión de control en servicios

## Mantenimiento

### Limpieza de Sesiones

```bash
# Limpieza manual
curl -X DELETE http://localhost:5002/api/hardware-auth/cleanup

# Limpieza automática (recomendado implementar con cron)
0 */1 * * * curl -X DELETE http://localhost:5002/api/hardware-auth/cleanup
```

### Monitoreo

```bash
# Sesiones activas
curl http://localhost:5002/api/hardware-auth/sessions

# Información del sistema
curl http://localhost:5002/api/hardware-auth/info
```

## Troubleshooting

### Problemas Comunes

1. **Token expirado**:
   - Renovar token antes de expiración
   - Implementar manejo de errores 401

2. **Hardware no encontrado**:
   - Verificar que el hardware esté activo
   - Verificar que pertenezca a la empresa

3. **Empresa inactiva**:
   - Verificar estado de la empresa
   - Contactar administrador

4. **Sede no encontrada**:
   - Verificar que la sede exista en la empresa
   - Verificar ortografía exacta

### Logs de Depuración

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Changelog

### v1.0.0
- ✅ Implementación inicial
- ✅ Endpoint único de autenticación
- ✅ Tokens JWT con expiración
- ✅ Gestión de sesiones
- ✅ Principios SOLID aplicados
- ✅ Documentación completa
- ✅ Pruebas automatizadas
