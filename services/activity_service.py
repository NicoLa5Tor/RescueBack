from repositories.activity_repository import ActivityRepository
from repositories.empresa_repository import EmpresaRepository

class ActivityService:
    """Servicio para registrar y consultar actividad de empresas."""

    def __init__(self):
        self.repo = ActivityRepository()
        # Se utiliza EmpresaRepository para obtener el nombre de la empresa
        self.empresa_repo = EmpresaRepository()

    def log(self, empresa_id: str, method: str, endpoint: str) -> None:
        try:
            self.repo.log(empresa_id, method, endpoint)
        except Exception as exc:
            print(f"Error registrando actividad: {exc}")

    def get_all(self):
        try:
            logs = self.repo.get_all()
            for log in logs:
                empresa_id = log.get("empresa_id")
                if empresa_id:
                    empresa = self.empresa_repo.find_by_id(empresa_id)
                    log["empresa_nombre"] = empresa.nombre if empresa else None
            return {"success": True, "data": logs}
        except Exception as exc:
            return {"success": False, "errors": [str(exc)]}

    def get_by_empresa(self, empresa_id: str):
        try:
            logs = self.repo.get_by_empresa(empresa_id)
            empresa = self.empresa_repo.find_by_id(empresa_id)
            nombre = empresa.nombre if empresa else None
            for log in logs:
                log["empresa_nombre"] = nombre
            return {"success": True, "data": logs}
        except Exception as exc:
            return {"success": False, "errors": [str(exc)]}
