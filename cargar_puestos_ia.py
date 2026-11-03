#!/usr/bin/env python3
"""Carga única: partidas de coste y puestos de ChatGPT en el proyecto "Paso de cuentas de IA compartidas a nominales".
Uso: .venv/bin/python cargar_puestos_ia.py   — no toca el proyecto si ya tiene partidas.
"""
import json, os, sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / os.getenv("DB_FILE", "actividad.db")
PID = "p-cuentas-nominales"

PARTIDAS = [
    {"concepto": "ChatGPT Business — puesto Estándar", "unidades": 43, "precio": 240, "periodo": "año"},
    {"concepto": "ChatGPT Business — puesto Prémium", "unidades": 1, "precio": 1200, "periodo": "año"},
]
PUESTOS = [
    {
        "email": "administracionsgp@serviplana.es",
        "tipo": "Estándar",
        "fecha": "2024-12-11"
    },
    {
        "email": "apastor@logiplana.es",
        "tipo": "Estándar",
        "fecha": "2025-02-27"
    },
    {
        "email": "alozano@serviplana.es",
        "tipo": "Estándar",
        "fecha": "2026-09-24"
    },
    {
        "email": "alpedernera@stnceramica.es",
        "tipo": "Estándar",
        "fecha": "2026-09-23"
    },
    {
        "email": "amachordom@stnceramica.es",
        "tipo": "Estándar",
        "fecha": "2026-10-15"
    },
    {
        "email": "djimenez@serviplana.es",
        "tipo": "Estándar",
        "fecha": "2026-10-15"
    },
    {
        "email": "drosell@serviplana.es",
        "tipo": "Estándar",
        "fecha": "2026-09-23"
    },
    {
        "email": "informatica@serviplana.es",
        "tipo": "Estándar",
        "fecha": "2024-11-07"
    },
    {
        "email": "dtomas@serviplana.es",
        "tipo": "Estándar",
        "fecha": "2026-09-23"
    },
    {
        "email": "esanchez@serviplana.es",
        "tipo": "Estándar",
        "fecha": "2026-09-18"
    },
    {
        "email": "fribera@serviplana.es",
        "tipo": "Estándar",
        "fecha": "2026-09-24"
    },
    {
        "email": "garoca@serviplana.es",
        "tipo": "Estándar",
        "fecha": "2026-10-15"
    },
    {
        "email": "gvillar@stnceramica.es",
        "tipo": "Estándar",
        "fecha": "2026-10-27"
    },
    {
        "email": "amiralles@stnceramica.es",
        "tipo": "Estándar",
        "fecha": "2025-02-12"
    },
    {
        "email": "jcbarbera@stnceramica.es",
        "tipo": "Estándar",
        "fecha": "2025-04-14"
    },
    {
        "email": "jtirado@ktlceramica.com",
        "tipo": "Estándar",
        "fecha": "2026-09-07"
    },
    {
        "email": "laguilera@serviplana.es",
        "tipo": "Estándar",
        "fecha": "2026-09-23"
    },
    {
        "email": "lmateu@stnceramica.es",
        "tipo": "Estándar",
        "fecha": "2026-10-15"
    },
    {
        "email": "lmollon@serviplana.es",
        "tipo": "Estándar",
        "fecha": "2026-09-23"
    },
    {
        "email": "lperez@nuevaalaplana.es",
        "tipo": "Estándar",
        "fecha": "2026-09-28"
    },
    {
        "email": "mromeroa@serviplana.es",
        "tipo": "Estándar",
        "fecha": "2026-10-15"
    },
    {
        "email": "mccruz@vitacer.es",
        "tipo": "Estándar",
        "fecha": "2026-09-16"
    },
    {
        "email": "mrebolledo@serviplana.es",
        "tipo": "Prémium",
        "fecha": "2026-10-02"
    },
    {
        "email": "mnavarro@serviplana.es",
        "tipo": "Estándar",
        "fecha": "2026-10-26"
    },
    {
        "email": "nvila@serviplana.es",
        "tipo": "Estándar",
        "fecha": "2026-10-15"
    },
    {
        "email": "pdetomas@serviplana.es",
        "tipo": "Estándar",
        "fecha": "2026-09-24"
    },
    {
        "email": "pvalls@serviplana.es",
        "tipo": "Estándar",
        "fecha": "2026-10-30"
    },
    {
        "email": "pcueco@serviplana.es",
        "tipo": "Estándar",
        "fecha": "2026-09-17"
    },
    {
        "email": "pnavarro@stnceramica.es",
        "tipo": "Estándar",
        "fecha": "2026-10-16"
    },
    {
        "email": "prevencion@serviplana.es",
        "tipo": "Estándar",
        "fecha": "2026-03-30"
    },
    {
        "email": "r.aparici@stnceramica.es",
        "tipo": "Estándar",
        "fecha": "2026-09-07"
    },
    {
        "email": "rtorres@serviplana.es",
        "tipo": "Estándar",
        "fecha": "2026-10-21"
    },
    {
        "email": "rrhh@serviplana.es",
        "tipo": "Estándar",
        "fecha": "2026-03-23"
    },
    {
        "email": "sveral@venuxsurface.es",
        "tipo": "Estándar",
        "fecha": "2025-07-16"
    },
    {
        "email": "santiago.tirado@nuevaalaplana.es",
        "tipo": "Estándar",
        "fecha": "2026-10-01"
    },
    {
        "email": "sbeneyto@ktlceramica.com",
        "tipo": "Estándar",
        "fecha": "2026-09-08"
    },
    {
        "email": "sergio.gutierrez@nuevaalaplana.es",
        "tipo": "Estándar",
        "fecha": "2026-09-28"
    },
    {
        "email": "svazquez@nuevaalaplana.es",
        "tipo": "Estándar",
        "fecha": "2026-09-28"
    },
    {
        "email": "stncomercialgpt@stnceramica.es",
        "tipo": "Estándar",
        "fecha": "2025-06-04"
    },
    {
        "email": "tgualde@serviplana.es",
        "tipo": "Estándar",
        "fecha": "2026-10-15"
    },
    {
        "email": "trodriguez@stnceramica.es",
        "tipo": "Estándar",
        "fecha": "2026-10-15"
    },
    {
        "email": "vleon@serviplana.es",
        "tipo": "Estándar",
        "fecha": "2026-10-15"
    },
    {
        "email": "vperez@serviplana.es",
        "tipo": "Estándar",
        "fecha": "2026-10-19"
    },
    {
        "email": "varnaug@serviplana.es",
        "tipo": "Estándar",
        "fecha": "2025-03-05"
    }
]


def main():
    con = sqlite3.connect(DB_PATH)
    row = con.execute("SELECT body FROM docs WHERE coll='proyectos' AND id=?", (PID,)).fetchone()
    if not row:
        print("No existe el proyecto", PID); return
    p = json.loads(row[0])
    if p.get("partidas"):
        print("El proyecto ya tiene partidas; no se toca."); return
    p["moneda"] = "USD"; p["partidas"] = PARTIDAS; p["puestos"] = PUESTOS; p["impuestos"] = True
    p["presupuesto"] = sum(x["unidades"] * x["precio"] for x in PARTIDAS)
    p.setdefault("log", []).append({"fecha": "2026-11-03", "texto": "Inventario de puestos ChatGPT Business: 43 Estándar + 1 Prémium = 11.520 $/año + impuestos.", "estado": p.get("estado", "")})
    p["actualizado"] = datetime.now(timezone.utc).isoformat()
    con.execute("UPDATE docs SET body=? WHERE coll='proyectos' AND id=?", (json.dumps(p, ensure_ascii=False), PID))
    con.commit()
    print("Listo: %d partidas, %d puestos, presupuesto %s USD/año" % (len(PARTIDAS), len(PUESTOS), p["presupuesto"]))


if __name__ == "__main__":
    main()
