#!/usr/bin/env python3
"""Alta única del proyecto 'Roles Dynamics 365 F&O' (Sistemas e Infraestructura) con sus actuaciones. No toca el proyecto si ya existe."""
import json, os, sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / os.getenv("DB_FILE", "actividad.db")
PID = "p-sis-d365-roles"
PROYECTO = {
    "area": "sis", "nombre": "Roles Dynamics 365 F&O",
    "descripcion": "Definición y asignación de roles y perfiles de seguridad en Dynamics 365 Finance & Operations por área funcional, a partir del inventario de perfiles.",
    "modalidad": "Interno", "proveedor": "", "estado": "En curso", "avance": 56,
    "inicio": "2026-01-01", "fin": "", "moneda": "EUR", "presupuesto": None, "partidas": [], "recursos": "Sistemas e Infraestructura",
    "actuaciones": [
        {"nombre": "Inventario de perfiles", "avance": 100},
        {"nombre": "Logística", "avance": 100},
        {"nombre": "Coordinadora producto", "avance": 100},
        {"nombre": "Marketing", "avance": 80},
        {"nombre": "Administración comercial", "avance": 20},
        {"nombre": "Comercial", "avance": 20},
        {"nombre": "Calidad y servicios", "avance": 20},
        {"nombre": "Administración", "avance": 10},
    ],
    "hitos": [], "log": [{"fecha": "2026-11-25", "texto": "Estado por área: inventario, logística y coordinadora de producto al 100 %; marketing 80 %; administración comercial, comercial y calidad 20 %; administración 10 %.", "estado": "En curso"}],
    "notas": "Pendiente de completar: fechas de inicio/fin y si interviene algún proveedor (p. ej. Prodware).",
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
