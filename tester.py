from endpoint_test_client import EndpointTestClient
empresa_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MDczNzY3MSwianRpIjoiZWVhMzgzMzktNTRjNy00OTgxLTk4ZGEtNmJjODJmM2RmMzk0IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjY4NThjZTAzYjA0M2I1YzdkOGVjYWE0MCIsIm5iZiI6MTc1MDczNzY3MSwiY3NyZiI6ImRiOTU5NzlhLTllNzQtNDYyMC05Mjk4LTE2MjQ0OTI0NmI4MSIsImV4cCI6MTc1MDczODU3MSwiZW1haWwiOiIxQDIuY29tIiwidXNlcm5hbWUiOiJlbXByZXNhIiwicm9sZSI6ImVtcHJlc2EiLCJwZXJtaXNvcyI6WyIvYXBpL2VtcHJlc2FzIiwiL2VtcHJlc2FzIl19.xwdYRCJh1zYdRXOWK25X-Db5Yy8-HELAfP3hRzygfRk"
admin_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MDgyMzY1NCwianRpIjoiNGYwMzlkOTgtYzllYS00YTRlLWI2N2EtM2M4MzM1YzBhMjU2IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjY4NGNiNGRkNTRiNDZiNmZhMmM1OWYzOSIsIm5iZiI6MTc1MDgyMzY1NCwiY3NyZiI6IjZkNGI3MmZhLTM0YjAtNGUwZi1iNGQ1LWRkYzQ5NjZiODBiYiIsImV4cCI6MTc1MDgyNDU1NCwiZW1haWwiOiJhZG1pbkBleGFtcGxlLmNvbSIsInVzZXJuYW1lIjoiYWRtaW4wMSIsInJvbGUiOiJzdXBlcl9hZG1pbiIsInBlcm1pc29zIjpbIi9hcGkvdXNlcnMiLCIvYXBpL2VtcHJlc2FzIiwiL2FwaS9hZG1pbiIsIi9lbXByZXNhcyJdfQ.CtNU5uayrUCQGX4o3lE81hN7kb4h_pF-_UJsOrT_mdo"
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
#=================== botonera ======================#
def createBotonera():
  data = {
    "empresa_nombre" : "empresa",
    "color" : "verde"
  }
  print(obj.create_botonera(data=data).json())

createBotonera()