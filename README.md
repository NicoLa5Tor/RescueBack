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

El token devuelto debe enviarse en el encabezado `Authorization` usando el
formato `Bearer <token>` en los demás endpoints protegidos.

Si las credenciales son inválidas retorna `401` con `{"success": false, "errors": ["Credenciales inválidas"]}`.

## Usuarios `/api/users`

### `POST /api/users/`
Crea un usuario. Debe pertenecer a una empresa existente (la API valida que `empresa_id` corresponda a una empresa real) y debe incluir un número de teléfono. El campo `whatsapp_verify` siempre se crea en `false`.

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
  -H 'Authorization: Bearer <token>' \
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
curl http://localhost:5000/api/users/ \
  -H 'Authorization: Bearer <token>'
```

### `GET /api/users/<id>`
Obtiene un usuario por ID.

**Curl**
```bash
curl http://localhost:5000/api/users/<id> \
  -H 'Authorization: Bearer <token>'
```

### `PUT /api/users/<id>`
Actualiza un usuario. Si se proporciona un nuevo `empresa_id`, la API verifica que esa empresa exista.

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
  -H 'Authorization: Bearer <token>' \
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
curl -X DELETE http://localhost:5000/api/users/<id> \
  -H 'Authorization: Bearer <token>'
```

### `GET /api/users/age-range?min_age=18&max_age=30`
Busca usuarios por rango de edad.

**Curl**
```bash
curl "http://localhost:5000/api/users/age-range?min_age=18&max_age=30" \
  -H 'Authorization: Bearer <token>'
```

### `GET /api/users/buscar-por-telefono?telefono=<numero>`
Busca un usuario por su número de teléfono.

**Curl**
```bash
curl "http://localhost:5000/api/users/buscar-por-telefono?telefono=3001234567" \
  -H 'Authorization: Bearer <token>'
```
**Respuesta**
```json
{
  "success": true,
  "data": {
    "_id": "<id>",
    "name": "Juan",
    "email": "juan@example.com",
    "age": 25,
    "empresa_id": "<id_empresa>",
    "telefono": "3001234567",
    "whatsapp_verify": false
  }
}
```

## Empresas `/api/empresas`

### `POST /api/empresas/`
Crear empresa (requiere super admin). Las empresas actúan como usuarios con rol `empresa` y necesitan credenciales propias.

**Entrada JSON**
```json
{
  "nombre": "Mi Empresa",
  "descripcion": "Empresa de ejemplo",
  "ubicacion": "Bogotá",
  "sedes": ["Principal"],
  "username": "miempresa",
  "email": "empresa@example.com",
  "password": "secreto"
}
```

**Curl**
```bash
curl -X POST http://localhost:5000/api/empresas/ \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <token>' \
  -d '{"nombre":"Mi Empresa","descripcion":"Empresa de ejemplo","ubicacion":"Bogotá","sedes":["Principal"],"username":"miempresa","email":"empresa@example.com","password":"secreto"}'
```

### `GET /api/empresas/`
Obtiene todas las empresas.

**Curl**
```bash
curl http://localhost:5000/api/empresas/ \
  -H 'Authorization: Bearer <token>'
```

### `GET /api/empresas/<id>`
Obtiene empresa por ID.

**Curl**
```bash
curl http://localhost:5000/api/empresas/<id> \
  -H 'Authorization: Bearer <token>'
```

### `PUT /api/empresas/<id>`
Actualiza empresa. El super admin que la creó o la propia empresa pueden modificarla.

**Curl**
```bash
curl -X PUT http://localhost:5000/api/empresas/<id> \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <token>' \
  -d '{"descripcion":"Nueva desc","password":"nuevo","sedes":["Sucursal 1","Sucursal 2"]}'
```

### `DELETE /api/empresas/<id>`
Elimina empresa (super admin creador).

**Curl**
```bash
curl -X DELETE http://localhost:5000/api/empresas/<id> \
  -H 'Authorization: Bearer <token>'
```

### `GET /api/empresas/mis-empresas`
Empresas creadas por el super admin autenticado.

**Curl**
```bash
curl http://localhost:5000/api/empresas/mis-empresas \
  -H 'Authorization: Bearer <token>'
```

### `GET /api/empresas/buscar-por-ubicacion?ubicacion=<loc>`
Buscar por ubicación.

**Curl**
```bash
curl "http://localhost:5000/api/empresas/buscar-por-ubicacion?ubicacion=Bogotá"
```

### `GET /api/empresas/estadisticas`
Estadísticas de empresas (requiere token de super admin).

**Curl**
```bash
curl http://localhost:5000/api/empresas/estadisticas \
  -H 'Authorization: Bearer <token>'
```

### `GET /api/empresas/<empresa_id>/activity`
Registra y consulta la actividad de una empresa específica. Requiere token de empresa o de super admin.

**Curl**
```bash
curl http://localhost:5000/api/empresas/<empresa_id>/activity \
  -H 'Authorization: Bearer <token>'
```

## Administración `/api/admin`

### `GET /api/admin/activity`
Devuelve la actividad registrada de todas las empresas. Requiere token de administrador o super admin.

**Curl**
```bash
curl http://localhost:5000/api/admin/activity \
  -H 'Authorization: Bearer <token>'
```

### `GET /api/admin/activity-admin`
Devuelve la actividad registrada de todas las empresas solo cuando el token pertenece a un administrador.

**Curl**
```bash
curl http://localhost:5000/api/admin/activity-admin \
  -H 'Authorization: Bearer <token>'
```

### `GET /api/admin/distribution`
Distribución de empresas (token de admin o super admin).

**Curl**
```bash
curl http://localhost:5000/api/admin/distribution \
  -H 'Authorization: Bearer <token>'
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

## Hardware `/api/hardware`

Los dispositivos de hardware representan cualquier equipo físico, como botoneras o semáforos. Al crear uno se debe indicar `empresa_nombre`, `nombre` único, `tipo` y `sede`. La sede es obligatoria y debe existir dentro de las sedes de la empresa. Cualquier otro campo adicional se guarda en `datos`.
Los tipos de hardware permitidos se almacenan en la colección `hardware_types` y pueden administrarse mediante los endpoints `/api/hardware-types`.

### `POST /api/hardware/`
Crea un nuevo hardware.

**Curl**
```bash
curl -X POST http://localhost:5000/api/hardware/ \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <token>' \
  -d '{"empresa_nombre":"Mi Empresa","nombre":"HW1","tipo":"botonera","sede":"Principal"}'
```

### `GET /api/hardware/`
Obtiene todos los dispositivos registrados.

**Curl**
```bash
curl http://localhost:5000/api/hardware/ \
  -H 'Authorization: Bearer <token>'
```

### `GET /api/hardware/empresa/<empresa_id>`
Obtiene el hardware asociado a una empresa.

**Curl**
```bash
curl http://localhost:5000/api/hardware/empresa/<empresa_id> \
  -H 'Authorization: Bearer <token>'
```

### `GET /api/hardware/<id>`
Obtiene un dispositivo por ID.

**Curl**
```bash
curl http://localhost:5000/api/hardware/<id> \
  -H 'Authorization: Bearer <token>'
```

### `PUT /api/hardware/<id>`
Actualiza un hardware.

**Curl**
```bash
curl -X PUT http://localhost:5000/api/hardware/<id> \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <token>' 
  -d '{"nombre":"Nuevo","tipo":"semaforo"}'
```

### `DELETE /api/hardware/<id>`
Elimina lógicamente un hardware.

**Curl**
```bash
curl -X DELETE http://localhost:5000/api/hardware/<id> \
  -H 'Authorization: Bearer <token>'
```

## Tipos de Hardware `/api/hardware-types`

Permite consultar y administrar la lista de dispositivos soportados. Por defecto existen los tipos `botonera` y `semaforo`.

### `POST /api/hardware-types/`
Agrega un nuevo tipo.

**Curl**
```bash
curl -X POST http://localhost:5000/api/hardware-types/ \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <token>' \
  -d '{"nombre":"nuevo"}'
```

### `GET /api/hardware-types/`
Obtiene todos los tipos disponibles.

**Curl**
```bash
curl http://localhost:5000/api/hardware-types/ \
  -H 'Authorization: Bearer <token>'
```

### `GET /api/hardware-types/<id>`
Obtiene un tipo por ID.

**Curl**
```bash
curl http://localhost:5000/api/hardware-types/<id> \
  -H 'Authorization: Bearer <token>'
```

### `PUT /api/hardware-types/<id>`
Actualiza un tipo existente.

**Curl**
```bash
curl -X PUT http://localhost:5000/api/hardware-types/<id> \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <token>' \
  -d '{"nombre":"otro"}'
```

### `DELETE /api/hardware-types/<id>`
Elimina lógicamente un tipo.

**Curl**
```bash
curl -X DELETE http://localhost:5000/api/hardware-types/<id> \
  -H 'Authorization: Bearer <token>'
```

## Permisos por rol

Los permisos determinan a qué endpoints puede acceder cada tipo de usuario. Si un usuario no cuenta con una lista personalizada, se aplican los siguientes valores por defecto:

| Rol         | Endpoints permitidos |
|-------------|--------------------------------------------------------------|
| super_admin | `/api/users`, `/api/empresas`, `/api/admin`, `/empresas` |
| admin       | `/api/admin/activity`, `/api/admin/activity-admin`, `/api/admin/distribution`, `/api/empresas/<empresa_id>/activity` |
| empresa     | `/api/empresas`, `/empresas` |
