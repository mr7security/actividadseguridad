#!/usr/bin/env python3
"""Pone inicio 01/01/2026 (aproximado) a los proyectos de Sistemas que no tengan fecha de inicio. Idempotente."""
import json, os, sqlite3
from datetime import datetime, timezone
from pathlib import Path
BASE = Path(__file__).resolve().parent
DB_PATH = BASE / os.getenv("DB_FILE", "actividad.db")
con = sqlite3.connect(DB_PATH); n = 0
for pid, body in con.execute("SELECT id, body FROM docs WHERE coll='proyectos'").fetchall():
    p = json.loads(body)
    if p.get("area") == "sis" and not p.get("inicio"):
        p["inicio"] = "2026-01-01"
        if "Fecha de inicio aproximada" not in p.get("notas", ""):
            p["notas"] = (p.get("notas", "") + " Fecha de inicio aproximada (01/01/2026).").strip()
        p["actualizado"] = datetime.now(timezone.utc).isoformat()
        con.execute("UPDATE docs SET body=? WHERE coll='proyectos' AND id=?", (json.dumps(p, ensure_ascii=False), pid)); n += 1
con.commit(); print("Proyectos con fecha asignada:", n)
