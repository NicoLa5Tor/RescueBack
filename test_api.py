import requests

# URL del endpoint
url = " http://localhost:5000/api/empresas/684cbaf7431268eeb95b395b"

# Token JWT (debes reemplazarlo con el real)
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjg0Y2I0ZGQ1NGI0NmI2ZmEyYzU5ZjM5IiwidXN1YXJpbyI6ImFkbWluMDEiLCJub21icmUiOiJBZG1pbmlzdHJhZG9yIFByaW5jaXBhbCIsImVtYWlsIjoiYWRtaW5AZXhhbXBsZS5jb20iLCJyb2wiOiJzdXBlcl9hZG1pbiIsInRpcG8iOiJhZG1pbiIsImV4cCI6MTc0OTg4NjU4OCwiaWF0IjoxNzQ5ODU3Nzg4fQ.nGKV2gZGLxu2unRMCXYKiUmdOKXC5BxBNPQ6KB-qe_U"

# Datos de la empresa
payload = {
    "ubicacion": "Facatativà, Colombia",

}

# Headers incluyendo el token
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

# Enviar la solicitud POST
response = requests.put(url, json=payload, headers=headers)

# Mostrar la respuesta
print("Status Code:", response.status_code)
print("Respuesta:", response.json())
