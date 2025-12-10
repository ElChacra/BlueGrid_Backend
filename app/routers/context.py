from fastapi import APIRouter, HTTPException
from app.services.database import get_db_connection
import psycopg2.extras

router = APIRouter(tags=["Contexto"])

@router.get("/zonas")
def get_zonas():
    """Retorna la lista de sectores/zonas desde la base de datos"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cursor.execute("SELECT id_sector, nombre_sector FROM SECTORES ORDER BY id_sector")
        rows = cursor.fetchall()
        
        # Formatear para el frontend (id como string para <select>)
        return [
            {"id": str(r["id_sector"]), "name": r["nombre_sector"]} 
            for r in rows
        ]
    except Exception as e:
        print(f"Error cargando zonas: {e}")
        raise HTTPException(status_code=500, detail="Error al cargar zonas")
    finally:
        cursor.close()
        conn.close()