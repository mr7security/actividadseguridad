#!/usr/bin/env python3
"""Alta única del proyecto ManageEngine Endpoint Central a partir del plan de implementación v1.4 (11/08/2026).
Uso: .venv/bin/python cargar_endpoint_central.py   — no hace nada si el proyecto ya existe.
"""
import json, os, sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / os.getenv("DB_FILE", "actividad.db")
PID = "p-endpoint-central"

H = lambda fecha, nombre, hecho=True, aprox=False: {"fecha": fecha, "nombre": nombre, "hecho": hecho, "aprox": aprox}

PROYECTO = {
    "nombre": "Implantación de ManageEngine Endpoint Central",
    "descripcion": "Gestión centralizada de parches, vulnerabilidades e inventario del parque de 224 servidores del Grupo STN (Security Edition, on-premise en SRVMGENDPOINT). Primera etapa de 50 servidores completada; en Fase 6 (producción por tramos) e incorporación de los 25 equipos del Departamento de IT.",
    "modalidad": "Tercerizado", "proveedor": "720tec (partner de ManageEngine) · con Sistemas (M. Pitarch)",
    "estado": "En curso", "avance": 55,
    "inicio": "2026-04-03", "fin": "2026-10-10",
    "moneda": "EUR", "presupuesto": None,
    "partidas": [],
    "recursos": "720tec + Sistemas + Seguridad",
    "notas": "Licencia: 50 servidores (50/50 asignados) + 50 puntos de conexión (25 en uso), 4 técnicos; caduca el 20/05/2027. Fase 6 requiere ampliar licencia. Importe de la licencia pendiente de cargar como partida.",
    "hitos": [
        H("2026-04-24", "Fase 1 – Planificación y diseño"),
        H("2026-05-23", "Fase 2 – Instalación del servidor y consola (720tec)"),
        H("2026-05-27", "Fase 3 – Agentes en los 13 servidores iniciales"),
        H("2026-05-29", "Fase 4 – Configuración de módulos"),
        H("2026-06-30", "Fase 5 – Piloto validado, ampliación a 50 servidores"),
        H("2026-08-11", "Primera etapa completada: 50/50 servidores + 25 equipos de IT"),
        H("2026-09-30", "Fase 6 – Producción por tramos hasta 224 servidores", hecho=False),
        H("2026-10-10", "Fase 7 – Cierre y publicación de resultados", hecho=False),
    ],
    "log": [
        {"fecha": "2026-06-03", "texto": "Plan de implementación v1.0 redactado (alcance, inventario, licenciamiento).", "estado": "En curso"},
        {"fecha": "2026-08-11", "texto": "Plan v1.4: 75 sistemas administrados (50 servidores / 25 equipos), 53 en buen estado y 22 altamente vulnerables; 801 vulnerabilidades detectadas (250 explotables, 105 activamente explotadas, 71 zero-day); 2.716 parches instalados y 266 pendientes (41 críticos). 51 de 224 servidores incorporados.", "estado": "En curso"},
    ],
}


def main():
    con = sqlite3.connect(DB_PATH)
    if con.execute("SELECT 1 FROM docs WHERE coll='proyectos' AND id=?", (PID,)).fetchone():
        print("El proyecto ya existe; no se toca."); return
    p = dict(PROYECTO); p["actualizado"] = datetime.now(timezone.utc).isoformat()
    con.execute("INSERT INTO docs VALUES ('proyectos',?,?)", (PID, json.dumps(p, ensure_ascii=False)))
    con.commit(); print("Proyecto Endpoint Central creado con", len(p["hitos"]), "hitos.")


if __name__ == "__main__":
    main()
