import os
import base64
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from app.services.repository import guardar_feedback

router = APIRouter(tags=["Training"])
TEMP_DIR = "/code/temp_last_batch"

class FeedbackItem(BaseModel):
    ref_id: str
    valor_corregido: str

class FeedbackPayload(BaseModel):
    zona_id: int
    usuario_id: Optional[int] = 15
    correcciones: List[FeedbackItem]

def procesar_feedback(payload: FeedbackPayload):
    for item in payload.correcciones:
        # 1. Buscar imagen en cache temporal
        path = os.path.join(TEMP_DIR, f"{item.ref_id}.png")
        b64_img = None
        
        if os.path.exists(path):
            with open(path, "rb") as f:
                b64_img = base64.b64encode(f.read()).decode("utf-8")
        
        # 2. Guardar en BD (aunque no haya imagen, guardamos el dato)
        if b64_img:
            guardar_feedback(payload.zona_id, payload.usuario_id, item.valor_corregido, b64_img)

@router.post("/training/feedback")
def recibir_feedback(payload: FeedbackPayload, bg_tasks: BackgroundTasks):
    bg_tasks.add_task(procesar_feedback, payload)
    return {"status": "success", "msg": "Procesando feedback..."}