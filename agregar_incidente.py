#!/usr/bin/env python3
"""Alta rápida de un incidente de seguridad desde la terminal.

Uso:
  .venv/bin/python agregar_incidente.py --fecha 2026-11-04 --tipo Malware --sev Baja \
      --titulo "..." --desc "..." --ref "TM-2026-11-04" --estado Abierto [--mitre T1204.002,T1566.001] [--id mi-id]
Si ya existe un incidente con el mismo --id, lo actualiza.
"""
import argparse, json, os, sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / os.getenv("DB_FILE", "actividad.db")

ap = argparse.ArgumentParser()
ap.add_argument("--fecha", required=True); ap.add_argument("--tipo", required=True); ap.add_argument("--titulo", required=True)
ap.add_argument("--sev", default="Media", choices=["Baja", "Media", "Alta", "Crítica"])
ap.add_argument("--estado", default="Resuelto", choices=["Resuelto", "Abierto"])
ap.add_argument("--desc", default=""); ap.add_argument("--ref", default=""); ap.add_argument("--mitre", default="")
ap.add_argument("--id", default=None)
a = ap.parse_args()

iid = a.id or ("i" + datetime.now().strftime("%Y%m%d%H%M%S"))
body = {"fecha": a.fecha, "tipo": a.tipo, "severidad": a.sev, "ref": a.ref, "titulo": a.titulo, "descripcion": a.desc,
        "estado": a.estado, "origen": "manual", "cau_id": None, "auto": False, "aprox": False,
        "mitre": [t.strip().upper() for t in a.mitre.split(",") if t.strip()],
        "actualizado": datetime.now(timezone.utc).isoformat()}
con = sqlite3.connect(DB_PATH)
existe = con.execute("SELECT 1 FROM docs WHERE coll='incidentes' AND id=?", (iid,)).fetchone()
con.execute("INSERT OR REPLACE INTO docs VALUES ('incidentes',?,?)", (iid, json.dumps(body, ensure_ascii=False)))
con.commit()
print(("Actualizado" if existe else "Creado"), "incidente", iid, "-", a.titulo)
