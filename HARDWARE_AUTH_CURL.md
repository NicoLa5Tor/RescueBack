# Hardware Authentication System - CURL Examples

## Authentication

### Authenticate Hardware
```bash
curl -X POST http://localhost:5002/api/hardware-auth/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "hardware_nombre": "Sensor001",
    "empresa_nombre": "TechCorp",
    "sede": "Sede Principal"
  }'
```

### Verify Token
```bash
curl -X POST http://localhost:5002/api/hardware-auth/verify-token \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Get Active Sessions
```bash
curl http://localhost:5002/api/hardware-auth/sessions
```

### Cleanup Expired Sessions
```bash
curl -X DELETE http://localhost:5002/api/hardware-auth/cleanup
```

### Get System Info
```bash
curl http://localhost:5002/api/hardware-auth/info
```

## Alerts

### Process MQTT Message
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
