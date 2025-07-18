# Servicio de Búsqueda por Teléfono

## Descripción

El servicio de búsqueda por teléfono permite obtener información de una persona utilizando su número de teléfono. Este servicio **no requiere autenticación** y devuelve información básica como nombre, empresa, sede, etc.

## Características

- ✅ **Sin autenticación**: No requiere tokens o credenciales
- ✅ **Búsqueda rápida**: Búsqueda directa por número de teléfono
- ✅ **Información completa**: Devuelve nombre, empresa, sede, cédula, rol y email
- ✅ **Validación de datos**: Verifica que el teléfono sea válido
- ✅ **Códigos de estado HTTP**: Respuestas claras según el resultado

## Endpoint

### Buscar por Teléfono

```http
GET /api/phone-lookup?telefono=NUMERO_TELEFONO
```

**Parámetros de consulta:**
- `telefono` (string, obligatorio): Número de teléfono a buscar

**Respuesta exitosa (200):**
```json
{
    "success": true,
    "data": {
        "nombre": "Juan Pérez",
        "empresa": "TechCorp S.A.S.",
        "sede": "Sede Principal",
        "telefono": "3001234567",
        "cedula": "12345678",
        "rol": "Técnico",
        "email": "juan.perez@techcorp.com"
    }
}
```

**Usuario no encontrado (404):**
```json
{
    "success": false,
    "error": "Usuario no encontrado",
    "message": "No se encontró ningún usuario con el teléfono 3001234567"
}
```

**Parámetro faltante (400):**
```json
{
    "success": false,
    "error": "Parámetro requerido",
    "message": "El parámetro \"telefono\" es obligatorio"
}
```

**Error del servidor (500):**
```json
{
    "success": false,
    "error": "Error interno",
    "message": "Error al buscar información: [detalle del error]"
}
```

## Ejemplos de Uso

### Usando cURL

```bash
# Búsqueda exitosa
curl "http://localhost:5000/api/phone-lookup?telefono=3001234567"

# Usuario no encontrado
curl "http://localhost:5000/api/phone-lookup?telefono=9999999999"

# Parámetro faltante
curl "http://localhost:5000/api/phone-lookup"
```

### Usando Python

```python
import requests

def buscar_por_telefono(telefono):
    url = f"http://localhost:5000/api/phone-lookup?telefono={telefono}"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            user_info = data['data']
            print(f"Nombre: {user_info['nombre']}")
            print(f"Empresa: {user_info['empresa']}")
            print(f"Sede: {user_info['sede']}")
            
        elif response.status_code == 404:
            print("Usuario no encontrado")
            
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

# Ejemplo de uso
buscar_por_telefono("3001234567")
```

### Usando JavaScript (Fetch)

```javascript
async function buscarPorTelefono(telefono) {
    try {
        const response = await fetch(`http://localhost:5000/api/phone-lookup?telefono=${telefono}`);
        const data = await response.json();
        
        if (response.status === 200) {
            console.log('Usuario encontrado:', data.data);
            console.log(`Nombre: ${data.data.nombre}`);
            console.log(`Empresa: ${data.data.empresa}`);
            console.log(`Sede: ${data.data.sede}`);
        } else if (response.status === 404) {
            console.log('Usuario no encontrado');
        } else {
            console.log('Error:', data.message);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Ejemplo de uso
buscarPorTelefono("3001234567");
```

## Estructura de Datos

### Modelo de Respuesta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `nombre` | string | Nombre completo del usuario |
| `empresa` | string | Nombre de la empresa |
| `sede` | string | Nombre de la sede |
| `telefono` | string | Número de teléfono |
| `cedula` | string | Número de cédula |
| `rol` | string | Rol del usuario en la empresa |
| `email` | string | Correo electrónico (puede ser null) |

## Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| 200 | Éxito - Usuario encontrado |
| 400 | Solicitud incorrecta - Parámetro faltante |
| 404 | No encontrado - Usuario no existe |
| 500 | Error del servidor |

## Validaciones

1. **Teléfono obligatorio**: El parámetro `telefono` debe estar presente
2. **Teléfono no vacío**: El número no puede estar vacío o solo contener espacios
3. **Usuario activo**: Solo busca usuarios activos en el sistema
4. **Empresa activa**: Solo considera usuarios de empresas activas

## Casos de Uso

### 1. Verificación de Emergencia
```bash
# Verificar información de contacto en emergencia
curl "http://localhost:5000/api/phone-lookup?telefono=911123456"
```

### 2. Directorio Telefónico
```bash
# Buscar información de contacto
curl "http://localhost:5000/api/phone-lookup?telefono=3001234567"
```

### 3. Validación de Datos
```bash
# Verificar que un número pertenece a un usuario válido
curl "http://localhost:5000/api/phone-lookup?telefono=3009876543"
```

## Pruebas

### Script de Prueba

Para probar el servicio, ejecute:

```bash
python test_phone_lookup.py
```

Este script permite:
- Buscar por un teléfono específico
- Buscar por múltiples teléfonos
- Manejo de errores y casos extremos

### Casos de Prueba

1. **Teléfono válido existente**: Debe retornar información completa
2. **Teléfono no existente**: Debe retornar error 404
3. **Parámetro faltante**: Debe retornar error 400
4. **Teléfono vacío**: Debe retornar error 400
5. **Usuario inactivo**: No debe aparecer en los resultados
6. **Empresa inactiva**: No debe aparecer en los resultados

## Arquitectura

### Componentes

1. **PhoneLookupService**: Lógica de negocio para búsqueda
2. **PhoneLookupController**: Manejo de peticiones HTTP
3. **UsuarioRepository**: Acceso a datos de usuarios
4. **EmpresaRepository**: Acceso a datos de empresas

### Flujo de Datos

```
HTTP Request → Controller → Service → Repository → Database
                  ↓
HTTP Response ← Controller ← Service ← Repository ← Database
```

## Consideraciones de Seguridad

- **Sin autenticación**: El servicio es público por diseño
- **Información limitada**: Solo expone datos básicos de contacto
- **No información sensible**: No expone contraseñas o datos privados
- **Usuarios activos**: Solo busca en usuarios activos

## Configuración

No requiere configuración especial. El servicio utiliza:
- MongoDB para almacenamiento
- Flask para el servidor web
- Repositorios existentes para acceso a datos

## Mantenimiento

### Logs
Los errores se registran en los logs del servidor Flask.

### Monitoreo
- Tiempo de respuesta
- Tasa de éxito/error
- Volumen de búsquedas

### Optimización
- Índices en la base de datos para el campo `telefono`
- Cache para búsquedas frecuentes (futuro)

## Limitaciones

1. **Búsqueda exacta**: Solo busca por número exacto
2. **Sin paginación**: No aplica para búsquedas individuales
3. **Sin filtros**: No permite filtros adicionales
4. **Sin búsqueda parcial**: No busca por partes del número

## Roadmap

- [ ] Búsqueda por número parcial
- [ ] Cache de resultados
- [ ] Rate limiting
- [ ] Búsqueda por múltiples campos
- [ ] Logs de auditoría para búsquedas

## Soporte

Para problemas o preguntas sobre el servicio:
1. Revisar logs del servidor
2. Verificar conexión a MongoDB
3. Comprobar que existan usuarios con teléfonos en la base de datos
4. Ejecutar script de prueba para diagnóstico
