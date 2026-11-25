#!/usr/bin/env python3
"""Alta única del proyecto 'CPD Sede STN' (Sistemas e Infraestructura) con sus actuaciones. No toca el proyecto si ya existe."""
import json, os, sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / os.getenv("DB_FILE", "actividad.db")
PID = "p-sis-cpd-stn"
PROYECTO = {
    "area": "sis", "nombre": "CPD Sede STN",
    "descripcion": "Adecuación del centro de proceso de datos de la sede STN: obra física, cuadros eléctricos e iluminación, grupo electrógeno, control de accesos y conexión de red.",
    "modalidad": "Interno", "proveedor": "", "estado": "En curso", "avance": 47,
    "inicio": "2026-01-01", "fin": "", "moneda": "EUR", "presupuesto": None, "partidas": [], "recursos": "Sistemas e Infraestructura",
    "actuaciones": [
        {"nombre": "Adecuación física", "avance": 100},
        {"nombre": "Cuadros e iluminación", "avance": 50},
        {"nombre": "Grupo electrógeno", "avance": 75},
        {"nombre": "Control de accesos", "avance": 0},
        {"nombre": "Conexión de red", "avance": 10},
    ],
    "hitos": [], "log": [{"fecha": "2026-11-25", "texto": "Estado de actuaciones: adecuación física 100 %, cuadros e iluminación 50 %, grupo electrógeno 75 %, control de accesos 0 %, conexión de red 10 %.", "estado": "En curso"}],
    "notas": "Pendiente de completar: fechas de inicio/fin, proveedores y presupuesto de cada actuación.",
}


def main():
    con = sqlite3.connect(DB_PATH)
    if con.execute("SELECT 1 FROM docs WHERE coll='proyectos' AND id=?", (PID,)).fetchone():
        print("El proyecto ya existe; no se toca."); return
    p = dict(PROYECTO); p["actualizado"] = datetime.now(timezone.utc).isoformat()
    con.execute("INSERT INTO docs VALUES ('proyectos',?,?)", (PID, json.dumps(p, ensure_ascii=False))); con.commit()
    print("Creado:", p["nombre"], "con", len(p["actuaciones"]), "actuaciones.")


if __name__ == "__main__":
    main()
