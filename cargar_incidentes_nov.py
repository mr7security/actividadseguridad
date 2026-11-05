#!/usr/bin/env python3
"""Incidentes de noviembre 2026 cargados desde las conversaciones (idempotente).
- Añade el tipo "Incumplimiento de política" a la configuración si no existe.
- 04/11 LENOVO-PW0EF0GQ (dtorres): triage sin infección, software no autorizado (INF-SEC-2026-P09).
"""
import json, os, sqlite3, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / os.getenv("DB_FILE", "actividad.db")
TIPO = "Incumplimiento de política"

con = sqlite3.connect(DB_PATH)
row = con.execute("SELECT body FROM docs WHERE coll='config' AND id='general'").fetchone()
cfg = json.loads(row[0]) if row else {}
tipos = cfg.get("tipos") or []
if TIPO not in tipos:
    tipos.append(TIPO); cfg["tipos"] = tipos
    mitre = cfg.get("mitre") or {}; mitre.setdefault(TIPO, "T1204"); cfg["mitre"] = mitre
    cfg["actualizado"] = datetime.now(timezone.utc).isoformat()
    con.execute("INSERT OR REPLACE INTO docs VALUES ('config','general',?)", (json.dumps(cfg, ensure_ascii=False),)); con.commit()
    print("Tipo añadido:", TIPO)
con.close()

subprocess.run([sys.executable, str(BASE / "agregar_incidente.py"),
    "--id", "i-20261104-dtorres", "--fecha", "2026-11-04", "--tipo", TIPO, "--sev", "Baja", "--estado", "Resuelto",
    "--ref", "INF-SEC-2026-P09",
    "--titulo", "Triage de LENOVO-PW0EF0GQ (dtorres) por error del equipo: sin infección, software no autorizado",
    "--desc", "Revisados antivirus, 230 procesos, servicios, 55 tareas programadas, autoruns, persistencia WMI, conexiones, ficheros recientes y cuentas: sin indicios de infección; Trend Micro activo. Causa probable: Epic Games Launcher y cuenta Microsoft personal dados de alta el 01/11 (16:18–16:25); factor concurrente, actualización de Lenovo Vantage. Acciones: desinstalar Epic Games y retirar la cuenta personal (Sistemas), comunicar la política de uso aceptable (Seguridad), verificar UltraVNC, deshabilitar Administrador local o pasarlo a LAPS y revisar RDP, eliminar perfiles sin uso. Evidencias: Triage_20261104_1433.",
    "--mitre", "T1204"], check=True)
