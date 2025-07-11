# Hardware Authentication System - CURL Examples

## Authentication

### Authenticate Hardware (Cookie-based)
```bash
curl -X POST http://localhost:5002/api/hardware-auth/authenticate \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "hardware_nombre": "Sensor001",
    "empresa_nombre": "TechCorp",
    "sede": "Sede Principal"
  }'
```

### Regular User Login (Cookie-based)
```bash
curl -X POST http://localhost:5002/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "usuario": "admin",
    "password": "password123"
  }'
```

### Verify Token (using cookies)
```bash
curl -X POST http://localhost:5002/api/hardware-auth/verify-token \
  -b cookies.txt
```

### Get Active Sessions
```bash
curl http://localhost:5002/api/hardware-auth/sessions \
  -b cookies.txt
```

### Cleanup Expired Sessions
```bash
curl -X DELETE http://localhost:5002/api/hardware-auth/cleanup \
  -b cookies.txt
```

### Get System Info
```bash
curl http://localhost:5002/api/hardware-auth/info
```

## Alerts

### Logout (Hardware Auth)
```bash
curl -X POST http://localhost:5002/api/hardware-auth/logout \
  -b cookies.txt
```

### Logout (Regular Users)
```bash
curl -X POST http://localhost:5002/auth/logout \
  -b cookies.txt
```

## Alerts

### Process MQTT Message (using cookies)
```bash
curl -X POST http://localhost:5002/api/mqtt-alerts/process \
  -H "Content-Type: application/json" \
  -b cookies.txt \
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

## Notes

- **Cookies**: All authentication now uses secure HTTP-only cookies
- **Security**: Cookies have `HttpOnly`, `Secure`, and `SameSite=Strict` flags
- **Storage**: No tokens are stored in localStorage or sessionStorage
- **Expiration**: Hardware auth tokens expire in 5 minutes, regular user tokens in 24 hours
- **Cookie Names**: 
  - Hardware authentication: `hardware_auth_token`
  - Regular user authentication: `auth_token`
