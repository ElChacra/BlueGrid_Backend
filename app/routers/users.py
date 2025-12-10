from fastapi import APIRouter
from app.services.database import get_db_connection
import psycopg2.extras

router = APIRouter(tags=["Usuarios"])

@router.get("/users")
def listar_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cursor.execute("""
            SELECT u.id_usuario, u.nombre_completo, u.correo, r.nombre_rol 
            FROM USUARIOS u
            JOIN ROLES r ON u.fk_rol = r.id_rol
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()