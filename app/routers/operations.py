from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.motor_ia import procesar_registro_ocr
from app.services.repository import guardar_registro_completo

router = APIRouter(tags=["Operaciones"])

@router.post("/registros")
async def subir_registro(
    file: UploadFile = File(...),
    zona_id: int = Form(...),
    usuario_id: int = Form(15) # Default para pruebas
):
    try:
        contents = await file.read()
        res_ia = procesar_registro_ocr(contents)
        
        if res_ia.get("status") == "error":
            raise HTTPException(400, "No se pudo procesar la imagen (Puntos rojos no encontrados).")

        # Guardar en DB
        fake_url = f"uploads/{file.filename}"
        id_db = guardar_registro_completo(usuario_id, fake_url, res_ia, zona_id)

        return {
            "id": id_db,
            "estado": "pendiente_validacion",
            "zona_id": zona_id,
            "resultado_ia": res_ia
        }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(500, f"Error interno: {str(e)}")

@router.put("/registros/{id}/validacion")
def validar(id: int, payload: dict):
    return {"msg": "Validado", "id": id}