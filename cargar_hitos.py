#!/usr/bin/env python3
"""Carga inicial de hitos en los proyectos existentes (una sola vez).

Solo añade hitos a los proyectos que no tengan ninguno y corrige inicio/fin cuando se indica.
Uso: .venv/bin/python cargar_hitos.py   (con el servicio parado o en marcha, da igual: SQLite lo soporta)
"""
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / os.getenv("DB_FILE", "actividad.db")

H = lambda fecha, nombre, hecho=True, aprox=False: {"fecha": fecha, "nombre": nombre, "hecho": hecho, "aprox": aprox}

HITOS = {
    "p-sensores": {"inicio": "2026-08-01", "inicio_aprox": True, "fin": "2026-09-04", "hitos": [
        H("2026-08-31", "Primera versión publicada (environmental-dashboard)"),
        H("2026-09-04", "Repo dashboard-sensores en producción"),
        H("2026-10-02", "Boceto de la vista del CPD para TV"),
    ]},
    "p-reportes-erp": {"inicio": "2026-10-23", "fin": "2026-10-28", "hitos": [
        H("2026-10-23", "Conexión a la réplica de solo lectura del ERP"),
        H("2026-10-26", "Dashboard Flask con login y envío por Direct Send", aprox=True),
        H("2026-10-28", "Segundo reporte Ventas (Alb) y multi-reporte en producción"),
    ]},
    "p-cpd-tv": {"inicio": "2026-10-01", "hitos": [
        H("2026-10-02", "Boceto visual 1920×1080 del plano de la sala"),
        H("2026-12-15", "Integración de sondas, cámaras y cerradura", hecho=False, aprox=True),
    ]},
    "p-uso-ia": {"inicio": "2026-10-02", "hitos": [
        H("2026-10-02", "Boceto con datos simulados"),
        H("2026-10-07", "Repo dashboard-ia publicado"),
        H("2026-11-30", "Carga de datos reales de puestos y costes", hecho=False, aprox=True),
    ]},
    "p-cuentas-nominales": {"inicio": "2026-09-22", "hitos": [
        H("2026-09-22", "Solicitud de cuentas de IA nominativas (CAU 177678)"),
        H("2026-10-01", "Licencias Claude para el equipo de software (CAU 178865)"),
        H("2026-10-15", "Primera cuenta ChatGPT nominal creada (CAU 180104)"),
        H("2026-11-30", "Decisión sobre el salto a ChatGPT Enterprise", hecho=False, aprox=True),
    ]},
    "p-ai-act": {"inicio": "2026-09-01", "inicio_aprox": True, "fin": "2026-09-14", "hitos": [
        H("2026-09-14", "Matriz artículo × departamento (Excel)", aprox=True),
        H("2026-09-14", "Presentación a Gerencia (PPTX)", aprox=True),
    ]},
    "p-concienciacion": {"inicio": "2026-03-01", "inicio_aprox": True, "hitos": [
        H("2026-05-12", "Guía rápida: phishing del falso SharePoint (CAU 162813)"),
        H("2026-08-12", "Simulacros: contraseñas, datos, incidentes, IA"),
        H("2026-08-13", "Portal de formación en seguridad"),
        H("2026-08-22", "Campañas: phishing, smishing, personaje Pepe, GIFs", aprox=True),
    ]},
}


def main():
    con = sqlite3.connect(DB_PATH)
    now = datetime.now(timezone.utc).isoformat()
    cambiados = 0
    for pid, spec in HITOS.items():
        row = con.execute("SELECT body FROM docs WHERE coll='proyectos' AND id=?", (pid,)).fetchone()
        if not row:
            print(f"  (no existe {pid}, se omite)")
            continue
        p = json.loads(row[0])
        if p.get("hitos"):
            print(f"  {pid}: ya tiene hitos, no se toca")
            continue
        p["hitos"] = spec["hitos"]
        for k in ("inicio", "fin"):
            if spec.get(k):
                p[k] = spec[k]
        if spec.get("inicio_aprox"):
            p["notas"] = (p.get("notas", "") + " Fecha de inicio aproximada.").strip()
        p["actualizado"] = now
        con.execute("UPDATE docs SET body=? WHERE coll='proyectos' AND id=?", (json.dumps(p, ensure_ascii=False), pid))
        cambiados += 1
        print(f"  {pid}: {len(spec['hitos'])} hitos")
    con.commit()
    print(f"Listo: {cambiados} proyectos actualizados.")


if __name__ == "__main__":
    main()
