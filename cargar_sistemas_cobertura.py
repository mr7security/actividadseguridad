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
    "modalidad": "Interno", "proveedor": "", "estado": "En curso", "avance": 77,
    "inicio": "2026-01-01", "fin": "", "moneda": "EUR", "presupuesto": None, "partidas": [], "recursos": "Sistemas e Infraestructura",
    "actuaciones": [
        {"nombre": "Estudios", "avance": 100},
        {"nombre": "Revisar informes", "avance": 100},
        {"nombre": "Mejoras CL5", "avance": 30},
    ],
    "hitos": [], "log": [{"fecha": "2026-11-25", "texto": "Estudios e informes revisados al 100 %; mejoras en CL5 al 30 % aprox.", "estado": "En curso"}],
    "notas": "Pendiente de completar: sedes cubiertas, fechas, proveedor que hizo los estudios y presupuesto de las mejoras.",
}


def main():
    con = sqlite3.connect(DB_PATH)
    row = con.execute("SELECT body FROM docs WHERE coll='proyectos' AND id=?", (PID,)).fetchone()
    if row:
        p = json.loads(row[0])
        if p.get("actuaciones") == PROYECTO["actuaciones"]:
            print("El proyecto ya está al día; no se toca."); return
        p["actuaciones"] = PROYECTO["actuaciones"]; p["avance"] = PROYECTO["avance"]
        p.setdefault("log", []).append({"fecha": "2026-11-25", "texto": "Actualización: revisión de informes completada (100 %); mejoras en CL5 al 30 % aprox.", "estado": p.get("estado", "En curso")})
        p["actualizado"] = datetime.now(timezone.utc).isoformat()
        con.execute("UPDATE docs SET body=? WHERE coll='proyectos' AND id=?", (json.dumps(p, ensure_ascii=False), PID)); con.commit()
        print("Actualizado:", p["nombre"]); return
    p = dict(PROYECTO); p["actualizado"] = datetime.now(timezone.utc).isoformat()
    con.execute("INSERT INTO docs VALUES ('proyectos',?,?)", (PID, json.dumps(p, ensure_ascii=False))); con.commit()
    print("Creado:", p["nombre"], "con", len(p["actuaciones"]), "actuaciones.")


if __name__ == "__main__":
    main()
