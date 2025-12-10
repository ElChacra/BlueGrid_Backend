import os
import shutil
import cv2
import numpy as np
import base64
from app.services.processor import PlateProcessor
from app.services.ocr_core import TablillaTrOCRService

# Directorio temporal para compartir imágenes entre endpoints
# En Railway esto se borra al reiniciar, pero dura mientras la instancia vive.
TEMP_DIR = "/code/temp_last_batch"

class IAService:
    def __init__(self):
        self.seg = PlateProcessor()
        self.ocr = TablillaTrOCRService()

    def procesar_imagen(self, image_bytes):
        # 1. Limpieza de cache previo
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        os.makedirs(TEMP_DIR, exist_ok=True)

        # 2. Segmentación
        seg_res = self.seg.process_image(image_bytes)
        if seg_res.get("status") == "error":
            return {"status": "error", "matriz": []}

        # 3. OCR
        _, ocr_data = self.ocr.ocr_from_segmented_grid(seg_res)
        
        matriz = []
        for item in ocr_data:
            r, c, txt, b64 = item["row"], item["col"], item["text"], item["crop_b64"]
            
            # Guardar en disco para que 'training.py' lo encuentre
            ref_id = f"R{r}_C{c}"
            if b64:
                try:
                    path = os.path.join(TEMP_DIR, f"{ref_id}.png")
                    with open(path, "wb") as f:
                        f.write(base64.b64decode(b64))
                except: pass

            matriz.append({
                "fila": f"Fila {r+1}", # Etiqueta visual para frontend
                "col": c,
                "valor": txt,
                "confianza": 0.95,
                "ref_id": ref_id # ID clave para el feedback
            })
            
        return {"status": "procesado_ia_tablilla", "promedio_confianza": 0.9, "matriz": matriz}

motor = IAService()

def procesar_registro_ocr(file_bytes):
    return motor.procesar_imagen(file_bytes)