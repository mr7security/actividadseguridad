#!/usr/bin/env python3
"""Fechas de inicio de los proyectos de Sistemas (idempotente):
- Roles Dynamics 365 F&O: julio 2026
- Estudios de cobertura: octubre 2026
- Resto sin fecha: 01/01/2026 (aproximada)
"""
import json, os, sqlite3
from datetime import datetime, timezone
from pathlib import Path
BASE = Path(__file__).resolve().parent
DB_PATH = BASE / os.getenv("DB_FILE", "actividad.db")
FECHAS = {"p-sis-d365-roles": "2026-07-01", "p-sis-cobertura": "2026-10-01"}
con = sqlite3.connect(DB_PATH); n = 0
for pid, body in con.execute("SELECT id, body FROM docs WHERE coll='proyectos'").fetchall():
    p = json.loads(body)
    if p.get("area") != "sis":
        continue
    nuevo = FECHAS.get(pid)
    if nuevo and p.get("inicio") != nuevo:
        p["inicio"] = nuevo; p["notas"] = (p.get("notas") or "").replace(" Fecha de inicio aproximada (01/01/2026).", "").strip()
    elif not nuevo and not p.get("inicio"):
        p["inicio"] = "2026-01-01"
        if "Fecha de inicio aproximada" not in p.get("notas", ""):
            p["notas"] = (p.get("notas", "") + " Fecha de inicio aproximada (01/01/2026).").strip()
    else:
        continue
    p["actualizado"] = datetime.now(timezone.utc).isoformat()
    con.execute("UPDATE docs SET body=? WHERE coll='proyectos' AND id=?", (json.dumps(p, ensure_ascii=False), pid)); n += 1
con.commit(); print("Proyectos actualizados:", n)
