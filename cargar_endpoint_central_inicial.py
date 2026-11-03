#!/usr/bin/env python3
"""Carga única de la licencia inicial de Endpoint Central (cot. 15374, 16/02/2026) en el proyecto.
Uso: .venv/bin/python cargar_endpoint_central_inicial.py — no duplica si ya está.
"""
import json, os, sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / os.getenv("DB_FILE", "actividad.db")
PID = "p-endpoint-central"
PARTIDAS = [
    {"concepto": "Cot. 15374 (16/02/2026) — licencia inicial: 50 servidores + 2 usuarios + ML Pack", "unidades": 1, "precio": 2654.20, "periodo": "año, hasta 20/05/2027"},
    {"concepto": "Cot. 15374 (16/02/2026) — jornada de formación del producto", "unidades": 1, "precio": 420.00, "periodo": "único"},
]
HITO = {"fecha": "2026-02-16", "nombre": "Cotización inicial 720tec: Control de servidores on-premise, Fase 1 (cot. 15374)", "hecho": True, "aprox": False}


def main():
    con = sqlite3.connect(DB_PATH)
    row = con.execute("SELECT body FROM docs WHERE coll='proyectos' AND id=?", (PID,)).fetchone()
    if not row:
        print("No existe el proyecto; ejecuta antes cargar_endpoint_central.py"); return
    p = json.loads(row[0])
    conceptos = {x.get("concepto") for x in p.get("partidas", [])}
    nuevas = [x for x in PARTIDAS if x["concepto"] not in conceptos]
    if not nuevas:
        print("La licencia inicial ya está cargada; no se toca."); return
    p["partidas"] = nuevas + p.get("partidas", [])
    p["moneda"] = "EUR"; p["impuestos"] = True
    p["presupuesto"] = round(sum((x.get("precio") or 0) * (x.get("unidades") or 0) for x in p["partidas"]), 2)
    if HITO["nombre"] not in {h.get("nombre") for h in p.get("hitos", [])}:
        p["hitos"] = p.get("hitos", []) + [HITO]
    p["notas"] = (p.get("notas", "")
                  .replace("La licencia inicial (50 servidores + 50 equipos + 4 técnicos) no tiene cotización en el dashboard. ", "")
                  + " Coste total del proyecto con la licencia inicial: 12.712,94 € sin IVA (15.382,65 € con IVA).")
    p["log"] = p.get("log", []) + [{"fecha": "2026-11-03", "texto": "Cargada la licencia inicial (cot. 15374, 16/02/2026): 2.654,20 €/año + 420 € de formación. Coste total del proyecto 12.712,94 € sin IVA.", "estado": p.get("estado", "")}]
    p["actualizado"] = datetime.now(timezone.utc).isoformat()
    con.execute("UPDATE docs SET body=? WHERE coll='proyectos' AND id=?", (json.dumps(p, ensure_ascii=False), PID))
    con.commit()
    print("Listo: %d partidas, presupuesto %.2f EUR sin IVA." % (len(p["partidas"]), p["presupuesto"]))


if __name__ == "__main__":
    main()
