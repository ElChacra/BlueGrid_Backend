from app.services.database import get_db_connection

def guardar_registro_completo(usuario_id, url_imagen, resultado_ia, zona_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Insertar Cabecera (REGISTROS_OCR)
        sql_head = """
            INSERT INTO REGISTROS_OCR (fk_usuario_creador, fk_sector, url_imagen_original, estado_validacion, promedio_confianza)
            VALUES (%s, %s, %s, 'BORRADOR', %s) RETURNING id_registro
        """
        conf = resultado_ia.get("promedio_confianza", 0.0)
        cursor.execute(sql_head, (usuario_id, zona_id, url_imagen, conf))
        id_reg = cursor.fetchone()['id_registro']
        
        # 2. Insertar Detalles (DETALLES_CAPTURA)
        # Mapeo: Col 1=Nido, Col 2=Cueva, Col 3=CheckNido, Col 4=CheckCueva, Col 5=Pulpos
        matriz = resultado_ia.get("matriz", [])
        filas = {}
        
        for c in matriz:
            f = c["fila"] # 0-based index from IA
            if f not in filas: filas[f] = {"n":0, "c":0, "h":None, "p":0, "conf":0.9}
            
            val = str(c["valor"]).strip()
            # Intentar convertir a numero, si falla es 0
            val_num = int(val) if val.isdigit() else 0
            
            col = c["col"] # 0-based index from IA
            
            if col == 0: filas[f]["n"] = val_num        # N° Nidos
            elif col == 1: filas[f]["c"] = val_num      # N° Cuevas
            elif col == 2 and val: filas[f]["h"] = 'NIDO' # Check Nido
            elif col == 3 and val: filas[f]["h"] = 'CUEVA' # Check Cueva
            elif col == 4: filas[f]["p"] = val_num      # Total Pulpos

        sql_det = """
            INSERT INTO DETALLES_CAPTURA (fk_registro, fila_index, n_nidos, n_cuevas_cubiertas, captura_hembras_tipo, total_pulpos, confianza_fila)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        for f_idx, d in filas.items():
            # Convertimos índice 0-based a 1-based para la BD si se desea, o lo dejamos como orden visual
            cursor.execute(sql_det, (id_reg, f_idx + 1, d["n"], d["c"], d["h"], d["p"], d["conf"]))
            
        conn.commit()
        return id_reg
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def guardar_feedback(zona_id, usuario_id, label, image_b64):
    """Guarda la corrección en la tabla FEEDBACK_IA (v6.0)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
            INSERT INTO FEEDBACK_IA (fk_sector, fk_usuario, valor_corregido, imagen_recorte_b64)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (zona_id, usuario_id, label, image_b64))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"❌ Error guardando feedback: {e}")
    finally:
        cursor.close()
        conn.close()