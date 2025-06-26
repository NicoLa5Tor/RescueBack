from endpoint_test_client import EndpointTestClient
empresa_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MDczNzY3MSwianRpIjoiZWVhMzgzMzktNTRjNy00OTgxLTk4ZGEtNmJjODJmM2RmMzk0IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjY4NThjZTAzYjA0M2I1YzdkOGVjYWE0MCIsIm5iZiI6MTc1MDczNzY3MSwiY3NyZiI6ImRiOTU5NzlhLTllNzQtNDYyMC05Mjk4LTE2MjQ0OTI0NmI4MSIsImV4cCI6MTc1MDczODU3MSwiZW1haWwiOiIxQDIuY29tIiwidXNlcm5hbWUiOiJlbXByZXNhIiwicm9sZSI6ImVtcHJlc2EiLCJwZXJtaXNvcyI6WyIvYXBpL2VtcHJlc2FzIiwiL2VtcHJlc2FzIl19.xwdYRCJh1zYdRXOWK25X-Db5Yy8-HELAfP3hRzygfRk"
admin_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MDg3NTUwNywianRpIjoiNTEyMmYyNDYtMGRiNy00YWZlLTk4N2ItYjA2MDNhNjVjMDVkIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjY4NGNiNGRkNTRiNDZiNmZhMmM1OWYzOSIsIm5iZiI6MTc1MDg3NTUwNywiY3NyZiI6ImU1M2E4ODU1LThlN2EtNDMxZS05NDJjLTgxMjVlZjhhNDc0YiIsImV4cCI6MTc1MDg3NjQwNywiZW1haWwiOiJhZG1pbkBleGFtcGxlLmNvbSIsInVzZXJuYW1lIjoiYWRtaW4wMSIsInJvbGUiOiJzdXBlcl9hZG1pbiIsInBlcm1pc29zIjpbIi9hcGkvdXNlcnMiLCIvYXBpL2VtcHJlc2FzIiwiL2FwaS9hZG1pbiIsIi9lbXByZXNhcyJdfQ.Y8by7gGolb0TWig_ezurCLwZ053lmbzFb7DL3-Rkams"
obj = EndpointTestClient(token=admin_token)
#region usuarios
def getUsuarios():
  print(obj.get_users().json())
def getUser():
  print(obj.get_user(user_id="6858c9c26c7edf43083d09ac").json())
def createUsuario():
   data =  {
            "name": "Nicolas Pruebas",
            "email": "nicolas@example.com",
            "age": 25,
            "empresa_id": "6858ce03b043b5c7d8ecaa40",
            "telefono": "3103391854"
        }
   response = obj.create_user(data=data)
   print(response.json())
#region Empresa
def creatEmpresa():
  data = {
            "nombre": "Mi Empresa 3",
            "descripcion": "Empresa de ejemplo",
            "ubicacion": "Bogotá",
            "sedes": ["Principal","secundaria"],
            "username": "nicolaspruebas",
            "email": "empresa2@example.com",
            "password": "secreto"
        }
  print(obj.create_empresa(data=data).json())
  
def getEmpresas():
  print(obj.get_empresas().json())
def getEmpresasActivity():
  print(obj.get_empresa_activity(empresa_id="6858ce03b043b5c7d8ecaa40").json())
#=================== activity main, actividad de las empresas solo por superadmin====#
def getActividadEmpresas():
  print(obj.get_admin_activity().json())
#=================== hardware ======================#
def createHardware():
    data = {
        "empresa_nombre": "empresa",
        "nombre": "HW1",
        "tipo": "botonera",
        "sede": "principal"
    }
    print(obj.create_hardware(data=data).json())

createHardware()
