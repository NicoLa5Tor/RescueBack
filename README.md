# API de RescueBack

Esta API está construida con Flask y MongoDB.

## Autenticación

### `POST /auth/login`

Solicita iniciar sesión con un nombre de usuario o email y una contraseña. El
servidor devolverá un token JWT junto con los datos del usuario y la lista de
endpoints a los que tiene acceso según su rol.

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
    "permisos": [
      "/api/users",
      "/api/empresas",
      "/api/admin",
      "/empresas"
    ],
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
Crea un usuario. El usuario debe pertenecer a una empresa existente y
proporcionar un número de teléfono. El campo `whatsapp_verify` siempre se crea
en `false` por defecto.

**Entrada JSON** ejemplo:
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

Curl:
```bash
curl -X POST http://localhost:5000/api/users/ \
  -H 'Content-Type: application/json' \
  -d '{"name":"Juan","email":"juan@example.com","age":25,"empresa_id":"<id_empresa>","telefono":"3001234567"}'
```

### `GET /api/users/`
Obtiene todos los usuarios.

Respuesta:
```json
{
  "success": true,
  "data": [ ... ],
  "count": 1
}
```

Curl:
```bash
curl http://localhost:5000/api/users/
```

### `GET /api/users/<id>`
Obtiene un usuario por ID.

Curl:
```bash
curl http://localhost:5000/api/users/<id>
```

### `PUT /api/users/<id>`
Actualiza un usuario.

### `DELETE /api/users/<id>`
Elimina un usuario.

### `GET /api/users/age-range?min_age=18&max_age=30`
Busca usuarios por rango de edad.

## Empresas `/api/empresas`

### `POST /api/empresas/`
Crear empresa (requiere super admin).

### `GET /api/empresas/`
Obtiene todas las empresas.

### `GET /api/empresas/<id>`
Obtiene empresa por ID.

### `PUT /api/empresas/<id>`
Actualiza empresa (super admin creador).

### `DELETE /api/empresas/<id>`
Elimina empresa (super admin creador).

### `GET /api/empresas/mis-empresas`
Empresas creadas por el super admin autenticado.

### `GET /api/empresas/buscar-por-ubicacion?ubicacion=<loc>`
Buscar por ubicación.

### `GET /api/empresas/estadisticas`
Estadísticas de empresas.

## Administración `/api/admin`

### `GET /api/admin/activity`
Actividad general (token de admin).

### `GET /api/admin/distribution`
Distribución de empresas (token de admin).

### `GET /api/empresas/<empresa_id>/activity`
Actividad de una empresa específica (token de admin).

## Multi-tenant `/empresas`

Los usuarios creados en este apartado siempre deben pertenecer a una empresa
previamente existente y **no** cuentan con permisos para iniciar sesión en la
API. Su gestión se realiza únicamente a través de los endpoints listados a
continuación.

### `POST /empresas/<empresa_id>/usuarios`
Crear usuario para una empresa.

### `GET /empresas/<empresa_id>/usuarios`
Listar usuarios de una empresa.

### `GET /empresas/<empresa_id>/usuarios/<usuario_id>`
Obtener un usuario de una empresa.

### `PUT /empresas/<empresa_id>/usuarios/<usuario_id>`
Actualizar un usuario de una empresa.

### `DELETE /empresas/<empresa_id>/usuarios/<usuario_id>`
Eliminar un usuario de una empresa.

## Permisos por rol

Los permisos determinan a qué endpoints puede acceder cada tipo de usuario. Si un
usuario no cuenta con una lista personalizada, se aplican los siguientes valores
por defecto:

| Rol         | Endpoints permitidos                                                                       |
|-------------|---------------------------------------------------------------------------------------------|
| super_admin | `/api/users`, `/api/empresas`, `/api/admin`, `/empresas`                                    |
| admin       | `/api/admin/activity`, `/api/admin/distribution`, `/api/empresas/<empresa_id>/activity`     |
| empresa     | `/api/empresas`, `/empresas`                                                                |


