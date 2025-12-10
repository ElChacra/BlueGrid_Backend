import cv2
import numpy as np
import base64
from app.services import config

class PlateProcessor:
    def __init__(self):
        self.lower_red1 = np.array([0, 120, 70]); self.upper_red1 = np.array([10, 255, 255])
        self.lower_red2 = np.array([170, 120, 70]); self.upper_red2 = np.array([180, 255, 255])
        self.lower_blue = np.array([90, 50, 50]); self.upper_blue = np.array([130, 255, 255])

    def _img_to_base64(self, img):
        if img is None or img.size == 0: return None
        _, buffer = cv2.imencode(".jpg", img)
        return base64.b64encode(buffer).decode("utf-8")

    def get_red_points(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_red1, self.upper_red1) + cv2.inRange(hsv, self.lower_red2, self.upper_red2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
        mask = cv2.dilate(mask, np.ones((5,5), np.uint8), iterations=2)
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:4]
        if len(cnts) < 4: return None
        centers = []
        for c in cnts:
            M = cv2.moments(c)
            if M["m00"] != 0: centers.append([int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"])])
        return np.array(centers)

    def order_points(self, pts):
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]; rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]; rect[3] = pts[np.argmax(diff)]
        return rect

    def force_rotate_and_align(self, img, pts):
        rect = cv2.minAreaRect(pts)
        (center, size, angle) = rect
        (w_rect, h_rect) = size
        if w_rect < h_rect:
            angle += 90
            if angle >= 180: angle -= 180
        else:
            if angle < -45: angle += 90
        
        (h, w) = img.shape[:2]
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        cos = np.abs(M[0, 0]); sin = np.abs(M[0, 1])
        nW = int((h * sin) + (w * cos)); nH = int((h * cos) + (w * sin))
        M[0, 2] += (nW / 2) - center[0]; M[1, 2] += (nH / 2) - center[1]
        rotated = cv2.warpAffine(img, M, (nW, nH), flags=cv2.INTER_LINEAR, borderValue=(255,255,255))
        
        check_pts = self.get_red_points(rotated)
        if check_pts is not None:
             check_rect = self.order_points(check_pts)
             w_f = np.linalg.norm(check_rect[0] - check_rect[1])
             h_f = np.linalg.norm(check_rect[0] - check_rect[3])
             if h_f > w_f:
                 rotated = cv2.rotate(rotated, cv2.ROTATE_90_COUNTERCLOCKWISE)
                 check_pts = self.get_red_points(rotated)
        
        # Orientación L/R
        if check_pts is not None:
            # Check simple de tinta a los lados
            rect = self.order_points(check_pts)
            tl, tr, _, _ = rect
            left_limit = int(tl[0]); right_limit = int(tr[0])
            if left_limit > 0 and right_limit < rotated.shape[1]:
                roi_l = rotated[:, max(0, left_limit-80):left_limit]
                roi_r = rotated[:, right_limit:min(rotated.shape[1], right_limit+80)]
                # Conteo básico de azul (tinta)
                hsv_l = cv2.cvtColor(roi_l, cv2.COLOR_BGR2HSV)
                hsv_r = cv2.cvtColor(roi_r, cv2.COLOR_BGR2HSV)
                mask_l = cv2.inRange(hsv_l, self.lower_blue, self.upper_blue)
                mask_r = cv2.inRange(hsv_r, self.lower_blue, self.upper_blue)
                if cv2.countNonZero(mask_r) > cv2.countNonZero(mask_l):
                    rotated = cv2.rotate(rotated, cv2.ROTATE_180)

        fh, fw = rotated.shape[:2]
        margin = 400
        canvas = np.ones((fh, fw + margin, 3), dtype=np.uint8) * 255
        canvas[:, :fw] = rotated
        return canvas

    def process_image(self, image_bytes):
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None: raise ValueError("Imagen corrupta")

        pts = self.get_red_points(img)
        if pts is None: return {"status": "error", "msg": "No se detectaron 4 puntos rojos", "grid": []}

        aligned = self.force_rotate_and_align(img, pts)
        new_pts = self.get_red_points(aligned)
        if new_pts is None: new_pts = pts; aligned = img # Fallback

        rect = self.order_points(new_pts)
        tl, tr, br, bl = rect
        
        start_x = int(tl[0]) + config.OFFSET_X
        start_y = int(tl[1]) + config.OFFSET_Y
        grid_height = int(bl[1] - tl[1])
        total_w = int(tr[0] - tl[0])
        row_h = grid_height // 5

        pixel_cuts = [start_x + int(total_w * pct) for pct in config.CORTES_PORCENTUALES]
        rows_res = []
        
        for r in range(5):
            y1 = start_y + (r * row_h); y2 = y1 + row_h
            cells = []
            for i in range(len(pixel_cuts)-1):
                x1 = pixel_cuts[i]; x2 = pixel_cuts[i+1]
                cells.append(self._img_to_base64(aligned[y1:y2, x1+4:x2-4]))
            rows_res.append({"row_index": r, "cells": cells})

        return {"status": "success", "grid": rows_res}