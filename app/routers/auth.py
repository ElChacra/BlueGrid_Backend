from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.database import get_db_connection
import psycopg2.extras

router = APIRouter(tags=["Autenticación"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/auth/login")
def login(creds: LoginRequest):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        # 1. Buscar usuario por username
        # NOTA: En producción real deberías usar hash (bcrypt), aquí comparamos texto plano
        # según tus datos semilla (1234).
        cursor.execute("""
            SELECT u.id_usuario, u.username, u.nombre_completo, u.password_hash, r.nombre_rol 
            FROM USUARIOS u
            JOIN ROLES r ON u.fk_rol = r.id_rol
            WHERE u.username = %s
        """, (creds.username,))
        
        user = cursor.fetchone()
        
        # 2. Validar contraseña
        if not user or user['password_hash'] != creds.password:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")
            
        # 3. Retornar estructura que espera tu App.tsx
        return {
            "access_token": f"mock-token-{user['id_usuario']}", # Token simulado
            "token_type": "bearer",
            "role": user['nombre_rol'], # 'admin', 'supervisor', 'buzo'
            "username": user['username'],
            "name": user['nombre_completo'],
            "id": user['id_usuario']
        }
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Error interno en login")
    finally:
        cursor.close()
        conn.close()