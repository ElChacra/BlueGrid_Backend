from fastapi import APIRouter

router = APIRouter(tags=["Audit"])

@router.get("/audit/logs")
def get_audit_logs():
    # Retorna una lista vacía o logs simulados por ahora
    return [
        {"id": 1, "action": "Sistema Iniciado", "timestamp": "2024-01-01 10:00:00"},
        {"id": 2, "action": "Base de datos conectada", "timestamp": "2024-01-01 10:00:05"}
    ]