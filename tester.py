from endpoint_test_client import EndpointTestClient
empresa_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MDcxMzY2NiwianRpIjoiMjljZWQ4ZjMtZmNlYi00ODQ5LTllNzEtYzVkYzMxYzhmY2FmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjY4NThjZTAzYjA0M2I1YzdkOGVjYWE0MCIsIm5iZiI6MTc1MDcxMzY2NiwiY3NyZiI6IjVkYjc2NmE1LWJmYzgtNDcwYi1iOTBhLTA2NDNlZTM5ZTk5OCIsImV4cCI6MTc1MDcxNDU2NiwiZW1haWwiOiIxQDIuY29tIiwidXNlcm5hbWUiOiJlbXByZXNhIiwicm9sZSI6ImVtcHJlc2EiLCJwZXJtaXNvcyI6WyIvYXBpL2VtcHJlc2FzIiwiL2VtcHJlc2FzIl19.7G8PVqO4_fXi4MB-xFr02XFoNnAX70OlFBfwM1ITEHE"
admin_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MDcxMzg2MSwianRpIjoiNDRiNjFkNjItM2UxYy00MjA3LTgxOGEtZGZiZTM2MjU4MTU5IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjY4NGNiNGRkNTRiNDZiNmZhMmM1OWYzOSIsIm5iZiI6MTc1MDcxMzg2MSwiY3NyZiI6IjEyNzQ5Y2JkLThjMDUtNGRkNS1hMjg0LWNhYjc5YTg3MWViYiIsImV4cCI6MTc1MDcxNDc2MSwiZW1haWwiOiJhZG1pbkBleGFtcGxlLmNvbSIsInVzZXJuYW1lIjoiYWRtaW4wMSIsInJvbGUiOiJzdXBlcl9hZG1pbiIsInBlcm1pc29zIjpbIi9hcGkvdXNlcnMiLCIvYXBpL2VtcHJlc2FzIiwiL2FwaS9hZG1pbiIsIi9lbXByZXNhcyJdfQ.Fawxb5D2d7tD75I5EO-8gF0cQLz47tEYSljtn8lplKM"
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


getUser()