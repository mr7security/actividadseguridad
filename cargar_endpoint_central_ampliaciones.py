#!/usr/bin/env python3
"""Carga única de las ampliaciones de licencia de Endpoint Central (cotizaciones 720tec) en el proyecto.
Uso: .venv/bin/python cargar_endpoint_central_ampliaciones.py — no hace nada si el proyecto ya tiene partidas.
"""
import json, os, sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / os.getenv("DB_FILE", "actividad.db")
PID = "p-endpoint-central"

PARTIDAS = [
    {"concepto": "Cot. 15919 (13/08/2026) — +50 servidores, +2 usuarios", "unidades": 1, "precio": 1970.16, "periodo": "hasta 20/05/2027"},
    {"concepto": "Cot. 15980 (27/08/2026) — +50 equipos, +3 usuarios", "unidades": 1, "precio": 1983.75, "periodo": "hasta 20/05/2027"},
    {"concepto": "Cot. 16159 (21/09/2026) — +100 equipos, +1 usuario", "unidades": 1, "precio": 2201.87, "periodo": "hasta 20/05/2027"},
    {"concepto": "Cot. 16346 (21/10/2026) — +200 equipos", "unidades": 1, "precio": 3482.96, "periodo": "hasta 20/05/2027"},
]
HITOS = [
    {"fecha": "2026-08-13", "nombre": "Ampliación +50 servidores, +2 usuarios (cot. 15919)", "hecho": True, "aprox": False},
    {"fecha": "2026-08-27", "nombre": "Ampliación +50 equipos, +3 usuarios (cot. 15980)", "hecho": True, "aprox": False},
    {"fecha": "2026-09-21", "nombre": "Ampliación +100 equipos, +1 usuario (cot. 16159)", "hecho": True, "aprox": False},
    {"fecha": "2026-10-21", "nombre": "Ampliación +200 equipos (cot. 16346)", "hecho": True, "aprox": False},
]
NOTAS = ("Licencia actual (Security Edition, hasta 20/05/2027): 100 servidores, 400 equipos, 9 técnicos. "
         "Partidas = ampliaciones contratadas a 720tec (importes sin IVA; con IVA 11.662,87 €). "
         "La licencia inicial (50 servidores + 50 equipos + 4 técnicos) no tiene cotización en el dashboard. "
         "Las cotizaciones suman 10 usuarios (4+2+3+1) frente a los 9 indicados: revisar.")
LOG = {"fecha": "2026-11-03", "texto": "Cargadas 4 ampliaciones de licencia (ago–oct 2026): 9.638,74 € sin IVA. Parque licenciado: 100 servidores, 400 equipos, 9 técnicos.", "estado": "En curso"}


def main():
    con = sqlite3.connect(DB_PATH)
    row = con.execute("SELECT body FROM docs WHERE coll='proyectos' AND id=?", (PID,)).fetchone()
    if not row:
        print("No existe el proyecto; ejecuta antes cargar_endpoint_central.py"); return
    p = json.loads(row[0])
    conceptos = {x.get("concepto") for x in p.get("partidas", [])}
    nuevas = [x for x in PARTIDAS if x["concepto"] not in conceptos]
    if not nuevas:
        print("Las 4 ampliaciones ya están cargadas; no se toca."); return
    p["moneda"] = "EUR"; p["partidas"] = p.get("partidas", []) + nuevas; p["impuestos"] = True
    p["presupuesto"] = round(sum((x.get("precio") or 0) * (x.get("unidades") or 0) for x in p["partidas"]), 2)
    nombres = {h.get("nombre") for h in p.get("hitos", [])}
    p["hitos"] = p.get("hitos", []) + [h for h in HITOS if h["nombre"] not in nombres]
    if "Cot. 15374" in str(p.get("partidas")):
        p["notas"] = NOTAS.replace("La licencia inicial (50 servidores + 50 equipos + 4 técnicos) no tiene cotización en el dashboard. ", "") + " Coste total del proyecto con la licencia inicial: 12.712,94 € sin IVA (15.382,65 € con IVA)."
    else:
        p["notas"] = NOTAS
    p["log"] = p.get("log", []) + [LOG]
    p["actualizado"] = datetime.now(timezone.utc).isoformat()
    con.execute("UPDATE docs SET body=? WHERE coll='proyectos' AND id=?", (json.dumps(p, ensure_ascii=False), PID))
    con.commit()
    print("Listo: %d partidas en total (%.2f EUR sin IVA), %d hitos." % (len(p["partidas"]), p["presupuesto"], len(p["hitos"])))


if __name__ == "__main__":
    main()
