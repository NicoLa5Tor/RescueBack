# 🚀 API Multi-Tenant con Flask y MongoDB

Sistema CRUD multi-tenant con autenticación JWT que permite a super administradores gestionar empresas y a las empresas gestionar sus propios usuarios.

## 📋 Índice

- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Autenticación](#-autenticación)
- [Endpoints de Empresas](#-endpoints-de-empresas)
- [Endpoints Multi-Tenant](#-endpoints-multi-tenant)
- [Ejemplos Completos](#-ejemplos-completos)
- [Códigos de Respuesta](#-códigos-de-respuesta)

## 🛠️ Instalación

```bash
# Clonar el repositorio
git clone <tu-repositorio>
cd api-multitenant

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones
```

## ⚙️ Configuración

### 1. Configurar MongoDB

```bash
# Iniciar MongoDB
mongod

# Conectarse a MongoDB
mongo
```

### 2. Crear Super Administrador

```javascript
// En MongoDB shell
use crud_app

db.administradores.insertOne({
  "usuario": "superadmin",
  "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdVAT5iOnE.ZdaC", // password: "admin123"
  "nombre": "Super Administrador",
  "email": "admin@sistema.com",
  "rol": "super_admin",
  "activo": true,
  "fecha_creacion": new Date(),
  "fecha_actualizacion": new Date(),
  "ultimo_login": null
})
```

### 3. Ejecutar la aplicación

```bash
python app.py
```

La API estará disponible en: `http://localhost:5000`

## 🔐 Autenticación

### Login como Super Administrador

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": "superadmin",
    "password": "admin123"
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "access": true,
  "message": "Login exitoso",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "usuario": "superadmin",
    "nombre": "Super Administrador",
    "email": "admin@sistema.com",
    "rol": "super_admin",
    "tipo": "admin",
    "permisos": ["crear_empresas", "editar_empresas", ...]
  }
}
```

### Verificar Token

```bash
curl -X POST http://localhost:5000/auth/verify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Renovar Token

```bash
curl -X POST http://localhost:5000/auth/refresh \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🏢 Endpoints de Empresas

> **Nota:** Todos los endpoints de gestión de empresas requieren autenticación de Super Administrador.

### 1. Crear Empresa

```bash
curl -X POST http://localhost:5000/api/empresas \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN" \
  -d '{
    "nombre": "TechCorp S.A.S",
    "descripcion": "Empresa de desarrollo de software y consultoría tecnológica",
    "ubicacion": "Bogotá, Colombia",
    "email": "contacto@techcorp.com",
    "password": "empresa123"
  }'
```

### 2. Listar Todas las Empresas

```bash
# Solo empresas activas (público)
curl -X GET http://localhost:5000/api/empresas

# Incluir empresas inactivas (solo admin)
curl -X GET "http://localhost:5000/api/empresas?include_inactive=true" \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN"
```

### 3. Obtener Empresa por ID

```bash
curl -X GET http://localhost:5000/api/empresas/507f1f77bcf86cd799439011
```

### 4. Actualizar Empresa

```bash
curl -X PUT http://localhost:5000/api/empresas/507f1f77bcf86cd799439011 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN" \
  -d '{
    "descripcion": "Empresa líder en transformación digital",
    "ubicacion": "Bogotá D.C., Colombia"
  }'
```

### 5. Eliminar Empresa

```bash
curl -X DELETE http://localhost:5000/api/empresas/507f1f77bcf86cd799439011 \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN"
```

### 6. Obtener Mis Empresas

```bash
curl -X GET http://localhost:5000/api/empresas/mis-empresas \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN"
```

### 7. Buscar Empresas por Ubicación

```bash
curl -X GET "http://localhost:5000/api/empresas/buscar-por-ubicacion?ubicacion=Bogotá"
```

### 8. Obtener Estadísticas

```bash
curl -X GET http://localhost:5000/api/empresas/estadisticas \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN"
```

## 👥 Endpoints Multi-Tenant

> **Nota:** Las empresas solo pueden gestionar sus propios usuarios. Los admins pueden gestionar cualquier empresa.

### 1. Login como Empresa

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "contacto@techcorp.com",
    "password": "empresa123"
  }'
```

### 2. Crear Usuario para Empresa

```bash
curl -X POST http://localhost:5000/empresas/507f1f77bcf86cd799439011/usuarios \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_EMPRESA_JWT_TOKEN" \
  -d '{
    "nombre": "Juan Pérez",
    "cedula": "12345678",
    "rol": "usuario"
  }'
```

**Roles válidos:** `admin`, `usuario`, `supervisor`, `operador`, `gerente`

### 3. Listar Usuarios de una Empresa

```bash
curl -X GET http://localhost:5000/empresas/507f1f77bcf86cd799439011/usuarios \
  -H "Authorization: Bearer YOUR_EMPRESA_JWT_TOKEN"
```

### 4. Obtener Usuario Específico

```bash
curl -X GET http://localhost:5000/empresas/507f1f77bcf86cd799439011/usuarios/507f1f77bcf86cd799439022 \
  -H "Authorization: Bearer YOUR_EMPRESA_JWT_TOKEN"
```

### 5. Actualizar Usuario

```bash
curl -X PUT http://localhost:5000/empresas/507f1f77bcf86cd799439011/usuarios/507f1f77bcf86cd799439022 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_EMPRESA_JWT_TOKEN" \
  -d '{
    "nombre": "Juan Carlos Pérez",
    "rol": "supervisor"
  }'
```

### 6. Eliminar Usuario

```bash
curl -X DELETE http://localhost:5000/empresas/507f1f77bcf86cd799439011/usuarios/507f1f77bcf86cd799439022 \
  -H "Authorization: Bearer YOUR_EMPRESA_JWT_TOKEN"
```

## 📖 Ejemplos Completos

### Flujo Completo: Admin Crea Empresa y Usuario

```bash
# 1. Login como admin
ADMIN_TOKEN=$(curl -s -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"usuario":"superadmin","password":"admin123"}' | \
  jq -r '.token')

# 2. Crear empresa
EMPRESA_RESPONSE=$(curl -s -X POST http://localhost:5000/api/empresas \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "nombre": "Empresa Demo",
    "descripcion": "Empresa de demostración",
    "ubicacion": "Medellín, Colombia",
    "email": "demo@empresa.com",
    "password": "empresa123"
  }')

EMPRESA_ID=$(echo $EMPRESA_RESPONSE | jq -r '.data._id')

# 3. Crear usuario para la empresa
curl -X POST http://localhost:5000/empresas/$EMPRESA_ID/usuarios \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "nombre": "María González",
    "cedula": "87654321",
    "rol": "gerente"
  }'
```

### Flujo Completo: Empresa Gestiona sus Usuarios

```bash
# 1. Login como empresa
EMPRESA_TOKEN=$(curl -s -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@empresa.com","password":"empresa123"}' | \
  jq -r '.token')

# 2. Obtener ID de la empresa del token
EMPRESA_ID=$(curl -s -X POST http://localhost:5000/auth/verify \
  -H "Authorization: Bearer $EMPRESA_TOKEN" | \
  jq -r '.payload.empresa_id')

# 3. Crear usuario
curl -X POST http://localhost:5000/empresas/$EMPRESA_ID/usuarios \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $EMPRESA_TOKEN" \
  -d '{
    "nombre": "Carlos Rodríguez",
    "cedula": "11223344",
    "rol": "operador"
  }'

# 4. Listar usuarios
curl -X GET http://localhost:5000/empresas/$EMPRESA_ID/usuarios \
  -H "Authorization: Bearer $EMPRESA_TOKEN"
```

## 📊 Códigos de Respuesta

| Código | Descripción | Cuándo Ocurre |
|--------|-------------|---------------|
| `200` | OK | Operación exitosa |
| `201` | Created | Recurso creado exitosamente |
| `400` | Bad Request | Datos inválidos o faltantes |
| `401` | Unauthorized | Token faltante o inválido |
| `403` | Forbidden | Sin permisos para la operación |
| `404` | Not Found | Recurso no encontrado |
| `500` | Internal Server Error | Error del servidor |

## 🔒 Sistema de Permisos

### Super Administrador
- ✅ Gestionar empresas (CRUD completo)
- ✅ Ver estadísticas globales
- ✅ Crear usuarios para cualquier empresa
- ✅ Acceso a datos inactivos

### Empresa
- ✅ Gestionar solo sus propios usuarios
- ✅ Ver solo sus propios datos
- ❌ No puede gestionar otras empresas
- ❌ No puede ver datos globales

## 🛡️ Validaciones

### Usuarios
- **Nombre:** 2-100 caracteres
- **Cédula:** 6-15 dígitos, única por empresa
- **Rol:** Debe ser uno de los roles válidos

### Empresas
- **Nombre:** 2-100 caracteres, único globalmente
- **Descripción:** 10-500 caracteres
- **Ubicación:** 3-200 caracteres
- **Email:** Formato válido, único para login

## 🔧 Variables de Entorno

```bash
# .env
MONGO_URI=mongodb://localhost:27017/
DATABASE_NAME=crud_app
SECRET_KEY=tu-clave-secreta
JWT_SECRET_KEY=tu-clave-jwt-super-secreta
DEBUG=True
HOST=0.0.0.0
PORT=5000
```

## 🚨 Troubleshooting

### Error de Conexión a MongoDB
```bash
# Verificar que MongoDB esté ejecutándose
sudo systemctl status mongod

# Iniciar MongoDB si está detenido
sudo systemctl start mongod
```

### Token Expirado
```bash
# Los tokens expiran en 8 horas. Renovar o hacer login nuevamente
curl -X POST http://localhost:5000/auth/refresh \
  -H "Authorization: Bearer YOUR_EXPIRED_TOKEN"
```

### Permisos Insuficientes
- Verificar que el token sea del tipo correcto (admin/empresa)
- Confirmar que la empresa esté intentando acceder solo a sus recursos

## 📝 Notas Adicionales

1. **Seguridad:** Todos los passwords se hashean con SHA-256 usando la SECRET_KEY
2. **Soft Delete:** Las eliminaciones son lógicas, no físicas
3. **Índices:** Se crean automáticamente para optimizar consultas
4. **CORS:** Habilitado para desarrollo (configurar para producción)
5. **Logs:** Revisar la consola para logs de depuración

---

Para más información o reportar bugs, contactar al equipo de desarrollo.