# API de Tipos de Empresa

Esta documentación describe los endpoints disponibles para la gestión de tipos de empresa en el sistema RescueBack.

## Base URL
```
http://localhost:5000/api
```

## Endpoints

### 1. Crear Tipo de Empresa
**POST** `/tipos_empresa`

Crea un nuevo tipo de empresa en el sistema.

#### Headers
```
Content-Type: application/json
```

#### Body
```json
{
    "nombre": "Tecnología",
    "descripcion": "Empresas de desarrollo de software, hardware y soluciones tecnológicas",
    "creado_por": "507f1f77bcf86cd799439011"
}
```

#### Respuesta Exitosa (201)
```json
{
    "success": true,
    "data": {
        "_id": "60f1b2c3d4e5f6g7h8i9j0k1",
        "nombre": "Tecnología",
        "descripcion": "Empresas de desarrollo de software, hardware y soluciones tecnológicas",
        "activo": true,
        "creado_por": "507f1f77bcf86cd799439011",
        "fecha_creacion": "2025-07-03T05:30:00.000Z",
        "fecha_actualizacion": "2025-07-03T05:30:00.000Z"
    }
}
```

#### Respuesta de Error (400)
```json
{
    "success": false,
    "errors": [
        "El nombre del tipo de empresa es obligatorio"
    ]
}
```

---

### 2. Obtener Tipo de Empresa por ID
**GET** `/tipos_empresa/{tipo_empresa_id}`

Obtiene un tipo de empresa específico por su ID.

#### Respuesta Exitosa (200)
```json
{
    "success": true,
    "data": {
        "_id": "60f1b2c3d4e5f6g7h8i9j0k1",
        "nombre": "Tecnología",
        "descripcion": "Empresas de desarrollo de software, hardware y soluciones tecnológicas",
        "activo": true,
        "creado_por": "507f1f77bcf86cd799439011",
        "fecha_creacion": "2025-07-03T05:30:00.000Z",
        "fecha_actualizacion": "2025-07-03T05:30:00.000Z"
    }
}
```

#### Respuesta de Error (404)
```json
{
    "success": false,
    "errors": [
        "Tipo de empresa no encontrado"
    ]
}
```

---

### 3. Obtener Todos los Tipos de Empresa
**GET** `/tipos_empresa`

Obtiene todos los tipos de empresa activos con paginación.

#### Parámetros de Query (opcionales)
- `skip`: Número de registros a saltar (default: 0)
- `limit`: Número máximo de registros a retornar (default: 100)

#### Ejemplo
```
GET /tipos_empresa?skip=0&limit=10
```

#### Respuesta Exitosa (200)
```json
{
    "success": true,
    "data": [
        {
            "_id": "60f1b2c3d4e5f6g7h8i9j0k1",
            "nombre": "Tecnología",
            "descripcion": "Empresas de desarrollo de software, hardware y soluciones tecnológicas",
            "activo": true,
            "creado_por": "507f1f77bcf86cd799439011",
            "fecha_creacion": "2025-07-03T05:30:00.000Z",
            "fecha_actualizacion": "2025-07-03T05:30:00.000Z"
        }
    ],
    "total": 1,
    "skip": 0,
    "limit": 10
}
```

---

### 4. Obtener Tipos de Empresa Activos (Simplificado)
**GET** `/tipos_empresa/activos`

Obtiene una lista simplificada de tipos de empresa activos, útil para dropdowns y selects.

#### Respuesta Exitosa (200)
```json
{
    "success": true,
    "data": [
        {
            "_id": "60f1b2c3d4e5f6g7h8i9j0k1",
            "nombre": "Tecnología"
        },
        {
            "_id": "60f1b2c3d4e5f6g7h8i9j0k2",
            "nombre": "Manufactura"
        }
    ]
}
```

---

### 5. Actualizar Tipo de Empresa
**PUT** `/tipos_empresa/{tipo_empresa_id}`

Actualiza un tipo de empresa existente.

#### Headers
```
Content-Type: application/json
```

#### Body
```json
{
    "nombre": "Tecnología Avanzada",
    "descripcion": "Empresas de desarrollo de software, hardware, IA y soluciones tecnológicas avanzadas"
}
```

#### Respuesta Exitosa (200)
```json
{
    "success": true,
    "data": {
        "_id": "60f1b2c3d4e5f6g7h8i9j0k1",
        "nombre": "Tecnología Avanzada",
        "descripcion": "Empresas de desarrollo de software, hardware, IA y soluciones tecnológicas avanzadas",
        "activo": true,
        "creado_por": "507f1f77bcf86cd799439011",
        "fecha_creacion": "2025-07-03T05:30:00.000Z",
        "fecha_actualizacion": "2025-07-03T05:35:00.000Z"
    }
}
```

---

### 6. Eliminar Tipo de Empresa
**DELETE** `/tipos_empresa/{tipo_empresa_id}`

Elimina lógicamente un tipo de empresa (soft delete).

#### Respuesta Exitosa (200)
```json
{
    "success": true,
    "message": "Tipo de empresa eliminado correctamente"
}
```

#### Respuesta de Error (404)
```json
{
    "success": false,
    "errors": [
        "Tipo de empresa no encontrado"
    ]
}
```

---

### 7. Buscar Tipos de Empresa
**GET** `/tipos_empresa/search`

Busca tipos de empresa por nombre o descripción.

#### Parámetros de Query
- `query`: Término de búsqueda (obligatorio)
- `skip`: Número de registros a saltar (default: 0)
- `limit`: Número máximo de registros a retornar (default: 100)

#### Ejemplo
```
GET /tipos_empresa/search?query=tecnologia&skip=0&limit=10
```

#### Respuesta Exitosa (200)
```json
{
    "success": true,
    "data": [
        {
            "_id": "60f1b2c3d4e5f6g7h8i9j0k1",
            "nombre": "Tecnología",
            "descripcion": "Empresas de desarrollo de software, hardware y soluciones tecnológicas",
            "activo": true,
            "creado_por": "507f1f77bcf86cd799439011",
            "fecha_creacion": "2025-07-03T05:30:00.000Z",
            "fecha_actualizacion": "2025-07-03T05:30:00.000Z"
        }
    ],
    "total": 1,
    "skip": 0,
    "limit": 10,
    "query": "tecnologia"
}
```

---

## Validaciones

### Campos obligatorios para creación:
- `nombre`: String (2-50 caracteres)
- `creado_por`: ObjectId válido del usuario creador

### Campos opcionales:
- `descripcion`: String (máximo 200 caracteres)

### Reglas de negocio:
- No pueden existir dos tipos de empresa con el mismo nombre
- Los nombres deben ser únicos (case insensitive)
- Al eliminar un tipo de empresa, se hace soft delete (activo = false)
- Solo se pueden obtener tipos de empresa activos en las consultas normales

---

## Códigos de Estado HTTP

- **200**: Operación exitosa
- **201**: Recurso creado exitosamente
- **400**: Error en los datos de entrada
- **404**: Recurso no encontrado
- **500**: Error interno del servidor

---

## Ejemplos de Uso con cURL

### Crear un tipo de empresa
```bash
curl -X POST http://localhost:5000/api/tipos_empresa \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Tecnología",
    "descripcion": "Empresas de desarrollo de software y hardware",
    "creado_por": "507f1f77bcf86cd799439011"
  }'
```

### Obtener todos los tipos de empresa
```bash
curl -X GET http://localhost:5000/api/tipos_empresa
```

### Buscar tipos de empresa
```bash
curl -X GET "http://localhost:5000/api/tipos_empresa/search?query=tecnologia"
```

### Obtener tipos activos para dropdown
```bash
curl -X GET http://localhost:5000/api/tipos_empresa/activos
```
