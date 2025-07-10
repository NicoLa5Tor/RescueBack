# Sistema de Alertas MQTT - Documentación

## Descripción General

El sistema de alertas MQTT procesa mensajes recibidos desde el servicio MqttConnection y los almacena en una colección MongoDB con información completa sobre el origen, ruta y metadatos adicionales.

## Estructura de la Colección `mqtt_alerts`

### Campos Principales

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `_id` | ObjectId | Identificador único |
| `empresa_nombre` | String | Nombre de la empresa |
| `sede` | String | Sede donde se generó la alerta |
| `tipo_alerta` | String | Tipo de alerta (semaforo, alarma, etc.) |
| `datos_hardware` | Object | Datos del hardware que generó la alerta |
| `mensaje_original` | Object | Mensaje MQTT original completo |
| `autorizado` | Boolean | **Estado de autorización** (false por defecto) |
| `estado_activo` | Boolean | **Estado activo** (true por defecto) |
| `usuario_autorizador` | ObjectId | ID del usuario que autorizó |
| `fecha_autorizacion` | DateTime | Fecha de autorización |
| `usuarios_notificados` | Array | Lista de usuarios con nombres y teléfonos |
| `data` | Object | **Metadatos adicionales y rutas** |
| `fecha_creacion` | DateTime | Fecha de creación |
| `fecha_actualizacion` | DateTime | Fecha de última actualización |

### Campo `data` - Metadatos y Rutas

El campo `data` contiene información adicional sobre el origen y procesamiento de la alerta:

```json
{
  "data": {
    "ruta_origen": "mqtt://empresas",
    "protocolo": "MQTT",
    "broker": "161.35.239.177:17090",
    "topic_completo": "empresas/empresa1",
    "timestamp_procesamiento": "2025-07-09T19:32:15.888351",
    "cliente_origen": "MqttConnection-Service",
    "metadatos": {
      "tamano_mensaje": 156,
      "tipo_procesamiento": "automatico",
      "nivel_prioridad": "media"
    }
  }
}
```

## Funcionalidades Implementadas

### 1. Verificación de Hardware (Filtro Inicial)

**Endpoint:** `GET /api/mqtt-alerts/verify-hardware?hardware_nombre=X`

- **FILTRO INICIAL**: Verifica si el hardware existe en la base de datos
- Si no existe: `autorizado=false`, `estado_activo=false`
- Si existe: procede a verificar empresa y sede

### 2. Verificación de Empresa y Sede

**Endpoint:** `GET /api/mqtt-alerts/verify-empresa-sede?empresa_nombre=X&sede=Y`

- Verifica si la empresa existe en la base de datos
- Verifica si la sede existe en esa empresa
- Retorna usuarios de esa empresa y sede con nombres y teléfonos

### 2. Procesamiento de Mensajes MQTT

**Endpoint:** `POST /api/mqtt-alerts/process`

Procesa mensajes con formato:
```json
{
  "empresa1": {
    "semaforo": {
      "sede": "principal",
      "alerta": "amarilla",
      "ubicacion": "Cruce principal",
      "hardware_id": "SEM001"
    }
  }
}
```

### 3. Gestión de Alertas

- **Listar alertas:** `GET /api/mqtt-alerts`
- **Ver alerta específica:** `GET /api/mqtt-alerts/<id>`
- **Prueba completa:** `GET /api/mqtt-alerts/test-flow`

## Ejemplo de Alerta Completa

```json
{
  "_id": "686ec3bf38fb57fc22eaea27",
  "empresa_nombre": "empresa1",
  "sede": "principal",
  "tipo_alerta": "semaforo",
  "datos_hardware": {
    "sede": "principal",
    "alerta": "amarilla",
    "ubicacion": "Cruce principal",
    "hardware_id": "SEM001",
    "coordenadas": {
      "lat": 4.6097,
      "lng": -74.0817
    }
  },
  "mensaje_original": {
    "empresa1": {
      "semaforo": {
        "sede": "principal",
        "alerta": "amarilla",
        "ubicacion": "Cruce principal",
        "hardware_id": "SEM001"
      }
    }
  },
  "autorizado": false,
  "estado_activo": true,
  "usuario_autorizador": null,
  "fecha_autorizacion": null,
  "usuarios_notificados": [
    {
      "nombre": "Juan Pérez",
      "telefono": "3001234567",
      "email": "juan@empresa1.com",
      "rol": "operador",
      "especialidades": ["semaforos", "mantenimiento"]
    }
  ],
  "data": {
    "ruta_origen": "mqtt://empresas",
    "protocolo": "MQTT",
    "broker": "161.35.239.177:17090",
    "topic_completo": "empresas/empresa1",
    "timestamp_procesamiento": "2025-07-09T19:32:15.888351",
    "cliente_origen": "MqttConnection-Service",
    "metadatos": {
      "tamano_mensaje": 156,
      "tipo_procesamiento": "automatico",
      "nivel_prioridad": "media"
    }
  },
  "fecha_creacion": "2025-07-09T19:32:15.893361",
  "fecha_actualizacion": "2025-07-09T19:32:15.893367"
}
```

## Niveles de Prioridad

El sistema calcula automáticamente la prioridad basándose en:

| Valor de Alerta | Prioridad |
|------------------|-----------|
| `roja`, `critica` | **critica** |
| `naranja` | **alta** |
| `amarilla`, `precaucion` | **media** |
| `verde`, `normal` | **baja** |

## Uso con el Cliente MQTT

El cliente MQTT escalable está configurado para enviar mensajes directamente a:
- **Endpoint:** `/api/mqtt-alerts/process`
- **Método:** POST
- **Formato:** JSON con estructura de empresas

## Estados de Alerta

### Lógica de Estados Según Verificación

#### Caso 1: Hardware NO existe
- `autorizado`: **false**
- `estado_activo`: **false**
- `usuarios_notificados`: **[]** (vacío)

#### Caso 2: Hardware existe pero empresa/sede NO
- `autorizado`: **false**
- `estado_activo`: **false**
- `usuarios_notificados`: **[]** (vacío)

#### Caso 3: Hardware, empresa y sede existen
- `autorizado`: **false** (pendiente de autorización)
- `estado_activo`: **true** (alerta activa)
- `usuarios_notificados`: **[usuarios de la sede]**

### Estados Fundamentales

1. **`autorizado`** (boolean)
   - `false`: Alerta pendiente de autorización
   - `true`: Alerta autorizada por un usuario

2. **`estado_activo`** (boolean)
   - `true`: Alerta activa y vigente
   - `false`: Alerta desactivada o resuelta

## Endpoints Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/mqtt-alerts/process` | Procesar mensaje MQTT |
| GET | `/api/mqtt-alerts` | Listar todas las alertas |
| GET | `/api/mqtt-alerts/<id>` | Obtener alerta específica |
| GET | `/api/mqtt-alerts/verify-hardware` | **Verificar hardware (filtro inicial)** |
| GET | `/api/mqtt-alerts/verify-empresa-sede` | Verificar empresa y sede |
| GET | `/api/mqtt-alerts/test-flow` | Probar flujo completo |

## Integración con el Sistema Existente

- ✅ **No afecta endpoints existentes**
- ✅ **Nueva colección independiente**
- ✅ **Utiliza modelos de Usuario y Empresa existentes**
- ✅ **Arquitectura escalable y modular**
