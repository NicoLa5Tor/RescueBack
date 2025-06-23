from bson import ObjectId
from datetime import datetime
from database import Database

class ActivityRepository:
    """Maneja el almacenamiento de logs de actividad."""

    def __init__(self):
        self.collection = Database().get_database().activity_logs
        self.collection.create_index([("empresa_id", 1)])
        self.collection.create_index([("timestamp", -1)])

    def log(self, empresa_id: str, method: str, endpoint: str) -> None:
        """Guarda un registro de actividad."""
        doc = {
            "empresa_id": ObjectId(empresa_id) if empresa_id else None,
            "method": method,
            "endpoint": endpoint,
            "timestamp": datetime.utcnow(),
        }
        self.collection.insert_one(doc)

    def _format(self, doc):
        return {
            "empresa_id": str(doc.get("empresa_id")) if doc.get("empresa_id") else None,
            "method": doc.get("method"),
            "endpoint": doc.get("endpoint"),
            "timestamp": doc.get("timestamp").isoformat() if doc.get("timestamp") else None,
        }

    def get_all(self, limit: int = 100):
        cursor = self.collection.find().sort("timestamp", -1).limit(limit)
        return [self._format(d) for d in cursor]

    def get_by_empresa(self, empresa_id: str, limit: int = 100):
        cursor = self.collection.find({"empresa_id": ObjectId(empresa_id)}).sort("timestamp", -1).limit(limit)
        return [self._format(d) for d in cursor]
