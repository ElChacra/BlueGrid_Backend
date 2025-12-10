import re
import cv2
import numpy as np
import base64
import pandas as pd
import torch
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

class TrOCRBackend:
    def __init__(self, model_name='microsoft/trocr-base-printed'):
        self.device = 'cpu' # Railway Free Tier no tiene GPU
        print(f"⬇️ Cargando modelo {model_name}...")
        self.processor = TrOCRProcessor.from_pretrained(model_name)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_name)
        self.model.to(self.device).eval()

    def _preprocess(self, cv2_img):
        if cv2_img is None: return None
        if cv2_img.ndim == 3: gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
        else: gray = cv2_img
        final_img = cv2.resize(gray, (384, 384), interpolation=cv2.INTER_AREA)
        return Image.fromarray(cv2.cvtColor(final_img, cv2.COLOR_GRAY2RGB))

    def _clean_text(self, text):
        if not text: return ""
        clean = "".join(re.findall(r"[0-9X]", text.upper()))
        return clean

    def predict_batch(self, image_list):
        if not image_list: return []
        pil_images = [self._preprocess(img) for img in image_list]
        pixel_values = self.processor(images=pil_images, return_tensors="pt").pixel_values.to(self.device)
        with torch.no_grad():
            generated_ids = self.model.generate(pixel_values, max_new_tokens=4)
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)
        return [self._clean_text(t) for t in generated_text]

class TablillaTrOCRService:
    def __init__(self):
        self.backend = TrOCRBackend()

    def ocr_from_segmented_grid(self, seg_json):
        grid = seg_json.get("grid", [])
        if not grid: return pd.DataFrame(), []

        cell_images = []
        coords = [] # (row, col)
        b64_list = []

        for row in grid:
            r_idx = row["row_index"]
            for c_idx, b64 in enumerate(row["cells"]):
                if not b64: continue
                nparr = np.frombuffer(base64.b64decode(b64), np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                cell_images.append(img)
                coords.append((r_idx, c_idx))
                b64_list.append(b64)

        if not cell_images: return pd.DataFrame(), []

        texts = self.backend.predict_batch(cell_images)
        ocr_data = []
        
        for (r, c), txt, b64 in zip(coords, texts, b64_list):
            ocr_data.append({
                "row": r, "col": c, "text": txt, "crop_b64": b64
            })
            
        return None, ocr_data # DataFrame no es estrictamente necesario aquí