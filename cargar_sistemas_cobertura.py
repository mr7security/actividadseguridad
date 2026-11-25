#!/usr/bin/env python3
"""Alta única del proyecto 'Estudios de cobertura' (Sistemas e Infraestructura) con sus actuaciones. No toca el proyecto si ya existe."""
import json, os, sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / os.getenv("DB_FILE", "actividad.db")
PID = "p-sis-cobertura"
PROYECTO = {
    "area": "sis", "nombre": "Estudios de cobertura",
    "descripcion": "Estudios de cobertura de red inalámbrica en las sedes: realización de los estudios, revisión de los informes y ejecución de las mejoras.",
    "modalidad": "Interno", "proveedor": "", "estado": "En curso", "avance": 33,
    "inicio": "", "fin": "", "moneda": "EUR", "presupuesto": None, "partidas": [], "recursos": "Sistemas e Infraestructura",
    "actuaciones": [
        {"nombre": "Estudios", "avance": 100},
        {"nombre": "Revisar informes", "avance": 0},
        {"nombre": "Mejoras", "avance": 0},
    ],
    "hitos": [], "log": [{"fecha": "2026-11-25", "texto": "Estudios realizados al 100 %; pendientes la revisión de informes y las mejoras.", "estado": "En curso"}],
    "notas": "Pendiente de completar: sedes cubiertas, fechas, proveedor que hizo los estudios y presupuesto de las mejoras.",
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
