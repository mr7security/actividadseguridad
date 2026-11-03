#!/usr/bin/env python3
"""Carga única de los puestos de Claude Team en el proyecto de cuentas nominales (partidas en EUR + usuarios). Idempotente."""
import json, os, sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / os.getenv("DB_FILE", "actividad.db")
PID = "p-cuentas-nominales"
PARTIDAS = [
    {"concepto": "Claude Team — puesto Estándar", "unidades": 9, "precio": 216, "moneda": "EUR", "periodo": "año"},
    {"concepto": "Claude Team — puesto Premium", "unidades": 3, "precio": 1080, "moneda": "EUR", "periodo": "año"},
]
PUESTOS = [
    ("informatica@serviplana.es", "Claude Estándar"), ("arivera@serviplana.es", "Claude Estándar"), ("acuecos@serviplana.es", "Claude Estándar"),
    ("dtomas@serviplana.es", "Claude Premium"), ("fribera@serviplana.es", "Claude Estándar"), ("fespinoza@serviplana.es", "Claude Premium"),
    ("lmollon@serviplana.es", "Claude Estándar"), ("maforner@serviplana.es", "Claude Estándar"), ("msubies@serviplana.es", "Claude Premium"),
    ("mmarti@serviplana.es", "Claude Estándar"), ("onavarro@serviplana.es", "Claude Estándar"), ("pdetomas@serviplana.es", "Claude Estándar"),
]


def main():
    con = sqlite3.connect(DB_PATH)
    row = con.execute("SELECT body FROM docs WHERE coll='proyectos' AND id=?", (PID,)).fetchone()
    if not row:
        print("No existe el proyecto", PID); return
    p = json.loads(row[0])
    if any(x.get("concepto", "").startswith("Claude Team") for x in p.get("partidas", [])):
        print("Los puestos de Claude ya están cargados; no se toca."); return
    # las partidas de ChatGPT pasan a llevar su moneda explícita (USD); el proyecto pasa a EUR
    for x in p.get("partidas", []):
        x.setdefault("moneda", p.get("moneda", "USD"))
    for u in p.get("puestos", []):
        if u.get("tipo") in ("Estándar", "Prémium"):
            u["tipo"] = "ChatGPT " + u["tipo"]
    p["partidas"] = p.get("partidas", []) + PARTIDAS
    p["puestos"] = p.get("puestos", []) + [{"email": e, "tipo": t, "fecha": ""} for e, t in PUESTOS]
    p["moneda"] = "EUR"
    p.setdefault("log", []).append({"fecha": "2026-11-03", "texto": "Inventario de puestos Claude Team: 9 Estándar (216 €/año) + 3 Premium (1.080 €/año) = 5.184 €/año + impuestos. Presupuesto del proyecto en euros (ChatGPT convertido con el tipo de cambio de Ajustes).", "estado": p.get("estado", "")})
    p["actualizado"] = datetime.now(timezone.utc).isoformat()
    con.execute("UPDATE docs SET body=? WHERE coll='proyectos' AND id=?", (json.dumps(p, ensure_ascii=False), PID))
    con.commit(); print("Listo: %d partidas, %d puestos." % (len(p["partidas"]), len(p["puestos"])))


if __name__ == "__main__":
    main()
