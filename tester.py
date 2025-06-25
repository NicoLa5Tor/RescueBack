from endpoint_test_client import EndpointTestClient
empresa_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MDczNzY3MSwianRpIjoiZWVhMzgzMzktNTRjNy00OTgxLTk4ZGEtNmJjODJmM2RmMzk0IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjY4NThjZTAzYjA0M2I1YzdkOGVjYWE0MCIsIm5iZiI6MTc1MDczNzY3MSwiY3NyZiI6ImRiOTU5NzlhLTllNzQtNDYyMC05Mjk4LTE2MjQ0OTI0NmI4MSIsImV4cCI6MTc1MDczODU3MSwiZW1haWwiOiIxQDIuY29tIiwidXNlcm5hbWUiOiJlbXByZXNhIiwicm9sZSI6ImVtcHJlc2EiLCJwZXJtaXNvcyI6WyIvYXBpL2VtcHJlc2FzIiwiL2VtcHJlc2FzIl19.xwdYRCJh1zYdRXOWK25X-Db5Yy8-HELAfP3hRzygfRk"
admin_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MDczNzcwOSwianRpIjoiMzE1YTA4NDUtMWYxYy00YTRkLTllNmMtNjRiYTM5ZjYxNmJlIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjY4NGNiNGRkNTRiNDZiNmZhMmM1OWYzOSIsIm5iZiI6MTc1MDczNzcwOSwiY3NyZiI6IjFhMWJmZmE4LWYwMTctNGRlZC04NjA3LWFlODc0ZGIyNjE0OCIsImV4cCI6MTc1MDczODYwOSwiZW1haWwiOiJhZG1pbkBleGFtcGxlLmNvbSIsInVzZXJuYW1lIjoiYWRtaW4wMSIsInJvbGUiOiJzdXBlcl9hZG1pbiIsInBlcm1pc29zIjpbIi9hcGkvdXNlcnMiLCIvYXBpL2VtcHJlc2FzIiwiL2FwaS9hZG1pbiIsIi9lbXByZXNhcyJdfQ.Uz80CHWsakisu4B_RLHEiqiw7AdiuNBwlJMNl3KUDoc"
obj = EndpointTestClient(token=admin_token)
#region useuarios
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
def getEmpresas():
  print(obj.get_empresas().json())
def getEmpresasActivity():
  print(obj.get_empresa_activity(empresa_id="6858ce03b043b5c7d8ecaa40").json())
#=================== activity main, actividad de las empresas solo por superadmin====#
def getActividadEmpresas():
  print(obj.get_admin_activity().json())

getActividadEmpresas()