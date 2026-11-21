import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'simtele.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql')

def get_connection():
    """Establece conexión con la base de datos SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa la base de datos aplicando el esquema relacional de 6 tablas."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada correctamente.")

def guardar_simulacion(escenario_id, usuario_equipo, ejecuciones):
    """
    Guarda una simulación completa con sus ejecuciones, iteraciones y resúmenes.
    :param escenario_id: ID del escenario (1: Detención, 2: Deterioro, etc.)
    :param usuario_equipo: Nombre del integrante o equipo
    :param ejecuciones: Lista de diccionarios con el detalle de los métodos ejecutados
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Insertar en tabla simulacion
    cursor.execute(
        "INSERT INTO simulacion (escenario_id, usuario_equipo, estado) VALUES (?, ?, ?)",
        (escenario_id, usuario_equipo, 'EXITOSO')
    )
    simulacion_id = cursor.lastrowid
    
    for ej in ejecuciones:
        # 2. Insertar en ejecucion_metodo
        cursor.execute(
            """INSERT INTO ejecucion_metodo 
               (simulacion_id, metodo, tolerancia, tiempo_ms, convergio) 
               VALUES (?, ?, ?, ?, ?)""",
            (simulacion_id, ej['metodo'], ej.get('tolerancia'), ej.get('tiempo_ms', 0.0), 1 if ej.get('convergio', True) else 0)
        )
        ejecucion_id = cursor.lastrowid
        
        # 3. Insertar historial de iteraciones en iteracion_resultado
        for it in ej.get('iteraciones', []):
            cursor.execute(
                """INSERT INTO iteracion_resultado 
                   (ejecucion_id, numero_iteracion, valor_x, residuo, error_abs, error_rel) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (ejecucion_id, it['k'], str(it['x']), it.get('residuo'), it.get('error_abs'), it.get('error_rel'))
            )
            
        # 4. Insertar resumen final en resultado_resumen
        cursor.execute(
            """INSERT INTO resultado_resumen 
               (ejecucion_id, valor_final_json, interpretacion, metricas_json) 
               VALUES (?, ?, ?, ?)""",
            (
                ejecucion_id,
                json.dumps(ej.get('valor_final')),
                ej.get('interpretacion', 'Simulación completada sin advertencias.'),
                json.dumps(ej.get('metricas', {}))
            )
        )
        
    conn.commit()
    conn.close()
    return simulacion_id

def obtener_historial_simulaciones(limit=10):
    """Recupera las últimas simulaciones registradas en el sistema."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, c.nombre AS modulo, e.tipo AS escenario, s.fecha, s.usuario_equipo, s.estado
        FROM simulacion s
        JOIN escenario e ON s.escenario_id = e.id
        JOIN caso_estudio c ON e.caso_id = c.id
        ORDER BY s.fecha DESC LIMIT ?
    """, (limit,))
    filas = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return filas