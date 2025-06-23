# API de RescueBack

Esta API está construida con Flask y MongoDB.

## Endpoints de salud

### `GET /health`
Devuelve el estado de la API.

**Respuesta**
```json
{
  "status": "OK",
  "message": "API funcionando correctamente",
  "database": "Connected"
}
```

**Curl**
```bash
curl http://localhost:5000/health
```

### `GET /`
Información básica de la API.

**Curl**
```bash
curl http://localhost:5000/
```

## Autenticación

### `POST /auth/login`
Solicita iniciar sesión con un nombre de usuario o email y una contraseña. El servidor devuelve un token JWT y los datos del usuario.

**Entrada JSON**
```json
{
  "usuario": "superadmin",
  "password": "secreto"
}
```

**Respuesta exitosa**
```json
{
  "success": true,
  "token": "<jwt>",
  "user": {
    "id": "<id>",
    "email": "admin@sistema.com",
    "username": "superadmin",
    "role": "super_admin",
    "permisos": ["/api/users","/api/empresas","/api/admin","/empresas"],
    "is_super_admin": true
  }
}
```

**Curl**
```bash
curl -X POST http://localhost:5000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"usuario":"superadmin","password":"secreto"}'
```

Si las credenciales son inválidas retorna `401` con `{"success": false, "errors": ["Credenciales inválidas"]}`.

## Usuarios `/api/users`

### `POST /api/users/`
Crea un usuario. El usuario debe pertenecer a una empresa existente y proporcionar un número de teléfono. El campo `whatsapp_verify` siempre se crea en `false`.

**Entrada JSON**
```json
{
  "name": "Juan",
  "email": "juan@example.com",
  "age": 25,
  "empresa_id": "<id_empresa>",
  "telefono": "3001234567"
}
```

**Respuesta**
```json
{
  "success": true,
  "message": "Usuario creado correctamente",
  "data": {
    "id": "<id>",
    "name": "Juan",
    "email": "juan@example.com",
    "age": 25,
    "empresa_id": "<id_empresa>",
    "telefono": "3001234567",
    "whatsapp_verify": false
  }
}
```

**Curl**
```bash
curl -X POST http://localhost:5000/api/users/ \
  -H 'Content-Type: application/json' \
  -d '{"name":"Juan","email":"juan@example.com","age":25,"empresa_id":"<id_empresa>","telefono":"3001234567"}'
```

### `GET /api/users/`
Obtiene todos los usuarios.

**Respuesta**
```json
{
  "success": true,
  "data": [ ... ],
  "count": 1
}
```

**Curl**
```bash
curl http://localhost:5000/api/users/
```

### `GET /api/users/<id>`
Obtiene un usuario por ID.

**Curl**
```bash
curl http://localhost:5000/api/users/<id>
```

### `PUT /api/users/<id>`
Actualiza un usuario.

**Entrada JSON** (cualquier campo de creación)
```json
{
  "name": "Nuevo Nombre",
  "email": "nuevo@email.com",
  "age": 30,
  "empresa_id": "<id_empresa>",
  "telefono": "3110000000",
  "whatsapp_verify": true
}
```

**Respuesta**
```json
{
  "success": true,
  "message": "Usuario actualizado correctamente",
  "data": { ... }
}
```

**Curl**
```bash
curl -X PUT http://localhost:5000/api/users/<id> \
  -H 'Content-Type: application/json' \
  -d '{"name":"Nuevo Nombre"}'
```

### `DELETE /api/users/<id>`
Elimina un usuario.

**Respuesta**
```json
{
  "success": true,
  "message": "Usuario eliminado correctamente"
}
```

**Curl**
```bash
curl -X DELETE http://localhost:5000/api/users/<id>
```

### `GET /api/users/age-range?min_age=18&max_age=30`
Busca usuarios por rango de edad.

**Curl**
```bash
curl "http://localhost:5000/api/users/age-range?min_age=18&max_age=30"
```

## Empresas `/api/empresas`

### `POST /api/empresas/`
Crear empresa (requiere super admin).

**Entrada JSON**
```json
{
  "nombre": "Mi Empresa",
  "descripcion": "Empresa de ejemplo",
  "ubicacion": "Bogotá"
}
```

**Curl**
```bash
curl -X POST http://localhost:5000/api/empresas/ \
  -H 'Content-Type: application/json' \
  -H 'X-Super-Admin-ID: <id_admin>' \
  -d '{"nombre":"Mi Empresa","descripcion":"Empresa de ejemplo","ubicacion":"Bogotá"}'
```

### `GET /api/empresas/`
Obtiene todas las empresas.

**Curl**
```bash
curl http://localhost:5000/api/empresas/
```

### `GET /api/empresas/<id>`
Obtiene empresa por ID.

**Curl**
```bash
curl http://localhost:5000/api/empresas/<id>
```

### `PUT /api/empresas/<id>`
Actualiza empresa (super admin creador).

**Curl**
```bash
curl -X PUT http://localhost:5000/api/empresas/<id> \
  -H 'Content-Type: application/json' \
  -H 'X-Super-Admin-ID: <id_admin>' \
  -d '{"nombre":"Nuevo nombre"}'
```

### `DELETE /api/empresas/<id>`
Elimina empresa (super admin creador).

**Curl**
```bash
curl -X DELETE http://localhost:5000/api/empresas/<id> \
  -H 'X-Super-Admin-ID: <id_admin>'
```

### `GET /api/empresas/mis-empresas`
Empresas creadas por el super admin autenticado.

**Curl**
```bash
curl http://localhost:5000/api/empresas/mis-empresas -H 'X-Super-Admin-ID: <id_admin>'
```

### `GET /api/empresas/buscar-por-ubicacion?ubicacion=<loc>`
Buscar por ubicación.

**Curl**
```bash
curl "http://localhost:5000/api/empresas/buscar-por-ubicacion?ubicacion=Bogotá"
```

### `GET /api/empresas/estadisticas`
Estadísticas de empresas (token de admin).

**Curl**
```bash
curl http://localhost:5000/api/empresas/estadisticas -H 'X-Super-Admin-ID: <id_admin>'
```

### `GET /api/empresas/<empresa_id>/activity`
Actividad de una empresa específica (token de admin).

**Curl**
```bash
curl http://localhost:5000/api/empresas/<empresa_id>/activity -H 'X-Admin-Token: <token>'
```

## Administración `/api/admin`

### `GET /api/admin/activity`
Actividad general (token de admin).

**Curl**
```bash
curl http://localhost:5000/api/admin/activity -H 'X-Admin-Token: <token>'
```

### `GET /api/admin/distribution`
Distribución de empresas (token de admin).

**Curl**
```bash
curl http://localhost:5000/api/admin/distribution -H 'X-Admin-Token: <token>'
```

## Multi-tenant `/empresas`
Los usuarios creados en este apartado pertenecen a una empresa y no pueden iniciar sesión en la API.

### `POST /empresas/<empresa_id>/usuarios`
Crear usuario para una empresa.

**Curl**
```bash
curl -X POST http://localhost:5000/empresas/<empresa_id>/usuarios \
  -H 'Content-Type: application/json' \
  -d '{"nombre":"Ana","cedula":"123456","rol":"operador"}'
```

### `GET /empresas/<empresa_id>/usuarios`
Listar usuarios de una empresa.

**Curl**
```bash
curl http://localhost:5000/empresas/<empresa_id>/usuarios
```

### `GET /empresas/<empresa_id>/usuarios/<usuario_id>`
Obtener un usuario de una empresa.

**Curl**
```bash
curl http://localhost:5000/empresas/<empresa_id>/usuarios/<usuario_id>
```

### `PUT /empresas/<empresa_id>/usuarios/<usuario_id>`
Actualizar un usuario de una empresa.

**Curl**
```bash
curl -X PUT http://localhost:5000/empresas/<empresa_id>/usuarios/<usuario_id> \
  -H 'Content-Type: application/json' \
  -d '{"nombre":"Nuevo"}'
```

### `DELETE /empresas/<empresa_id>/usuarios/<usuario_id>`
Eliminar un usuario de una empresa.

**Curl**
```bash
curl -X DELETE http://localhost:5000/empresas/<empresa_id>/usuarios/<usuario_id>
```

## Permisos por rol

Los permisos determinan a qué endpoints puede acceder cada tipo de usuario. Si un usuario no cuenta con una lista personalizada, se aplican los siguientes valores por defecto:

| Rol         | Endpoints permitidos |
|-------------|--------------------------------------------------------------|
| super_admin | `/api/users`, `/api/empresas`, `/api/admin`, `/empresas` |
| admin       | `/api/admin/activity`, `/api/admin/distribution`, `/api/empresas/<empresa_id>/activity` |
| empresa     | `/api/empresas`, `/empresas` |
