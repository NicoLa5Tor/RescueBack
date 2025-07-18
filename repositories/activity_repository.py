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
    
    def count_activity_by_empresa(self, empresa_id: str, period_days: int = 30) -> int:
        """Cuenta la actividad de una empresa en un período específico."""
        from datetime import datetime, timedelta
        
        # Calcular fecha límite
        start_date = datetime.utcnow() - timedelta(days=period_days)
        
        count = self.collection.count_documents({
            "empresa_id": ObjectId(empresa_id),
            "timestamp": {"$gte": start_date}
        })
        return count
    
    def get_activity_stats_by_empresa(self, period_days: int = 30):
        """Obtiene estadísticas de actividad agrupadas por empresa."""
        from datetime import datetime, timedelta
        
        # Calcular fecha límite
        start_date = datetime.utcnow() - timedelta(days=period_days)
        
        pipeline = [
            {
                "$match": {
                    "timestamp": {"$gte": start_date},
                    "empresa_id": {"$ne": None}
                }
            },
            {
                "$group": {
                    "_id": "$empresa_id",
                    "count": {"$sum": 1},
                    "last_activity": {"$max": "$timestamp"}
                }
            },
            {
                "$sort": {"count": -1}
            }
        ]
        
        result = list(self.collection.aggregate(pipeline))
        return result
