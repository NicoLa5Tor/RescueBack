from repositories.activity_repository import ActivityRepository

class ActivityService:
    """Servicio para registrar y consultar actividad de empresas."""

    def __init__(self):
        self.repo = ActivityRepository()

    def log(self, empresa_id: str, method: str, endpoint: str) -> None:
        try:
            self.repo.log(empresa_id, method, endpoint)
        except Exception as exc:
            print(f"Error registrando actividad: {exc}")

    def get_all(self):
        try:
            return {"success": True, "data": self.repo.get_all()}
        except Exception as exc:
            return {"success": False, "errors": [str(exc)]}

    def get_by_empresa(self, empresa_id: str):
        try:
            return {"success": True, "data": self.repo.get_by_empresa(empresa_id)}
        except Exception as exc:
            return {"success": False, "errors": [str(exc)]}
