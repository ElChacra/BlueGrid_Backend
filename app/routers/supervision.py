from fastapi import APIRouter
from app.services.database import get_db_connection
import psycopg2.extras

router = APIRouter(tags=["Supervision"])

@router.get("/dashboard/data")
def get_dashboard_data(zone_id: str = "all"):
    """
    Retorna KPIs. Calcula el total real desde la BD
    y devuelve estructura compatible con Dashboard.tsx
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Ejemplo: Contar total de pulpos registrados en la BD
        cursor.execute("SELECT COALESCE(SUM(total_pulpos), 0) FROM DETALLES_CAPTURA")
        total_pulpos = cursor.fetchone()[0]
        
        # Estructura que espera tu Dashboard.tsx (MOCK_DASHBOARD_DATA)
        return {
            "kpis": [
                { 
                    "id": "1", 
                    "label": "Captura Total (Real BD)", 
                    "value": str(total_pulpos), 
                    "trend": "up", 
                    "trendValue": "+Live", 
                    "iconName": "Octopus" 
                },
                { 
                    "id": "2", 
                    "label": "% Ocupación Cuevas", 
                    "value": "85%", 
                    "trend": "up", 
                    "trendValue": "+5%", 
                    "iconName": "Home" 
                },
                { 
                    "id": "3", 
                    "label": "Registros Procesados", 
                    "value": "12", 
                    "trend": "neutral", 
                    "trendValue": "0%", 
                    "iconName": "Activity" 
                }
            ],
            "barData": [
                { "name": "Lun", "value": 120 }, { "name": "Mar", "value": 150 }, 
                { "name": "Mie", "value": 180 }, { "name": "Jue", "value": 140 }, 
                { "name": "Vie", "value": 200 }
            ],
            "pieData": [
                { "name": "Machos", "value": 400 }, { "name": "Hembras", "value": 500 }
            ]
        }
    finally:
        cursor.close()
        conn.close()