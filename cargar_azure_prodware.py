#!/usr/bin/env python3
"""Alta única del proyecto Consultoría Azure / unificación de tenants (Prodware) a partir de las propuestas
Fase 1 (OPP000529073, 04/12/2025) y Fase 2 (OPP000532115, 11/03/2026). No hace nada si ya existe.
"""
import json, os, sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / os.getenv("DB_FILE", "actividad.db")
PID = "p-azure-prodware"
H = lambda fecha, nombre, hecho=True, aprox=False: {"fecha": fecha, "nombre": nombre, "hecho": hecho, "aprox": aprox}

PROYECTO = {
    "nombre": "Consultoría Azure: unificación de tenants (Prodware)",
    "descripcion": "Dos tenants con más de 800 recursos de Azure en 47 resource groups crecidos sin arquitectura ni gobierno. Fase 1: assessment de unificación de tenants (realizado). Fase 2: Assessment Azure Architecture Excellence, Landing Zone ad hoc (Hub & Spoke) y migración cross-tenant con IaC (Bicep, AzCopy, LCS para los 7 entornos de Dynamics 365 F&O), 8 semanas.",
    "modalidad": "Tercerizado", "proveedor": "Prodware Spain (M. Pastor, R. Cacho)",
    "estado": "En curso", "avance": 45,
    "inicio": "2025-11-13", "fin": "2026-12-06",
    "moneda": "EUR", "impuestos": True,
    "partidas": [
        {"concepto": "Fase 1 — Assessment unificación de tenants (OPP000529073, 04/12/2025)", "unidades": 1, "precio": 3220.00, "periodo": "único"},
        {"concepto": "Fase 2 — Ejecución unificación: AAE + Landing Zone + migración cross-tenant (OPP000532115, 11/03/2026, con descuento −1.615 €)", "unidades": 1, "precio": 28405.00, "periodo": "único"},
    ],
    "presupuesto": 31625.00,
    "recursos": "Prodware + Seguridad (M. Rebolledo) + Sistemas",
    "notas": "Importes sin IVA. Fase 2 factura 20 % a la firma, 60 % por avance mensual y 20 % al cierre. Fecha de fin tomada del vencimiento del CAU 154991 (aprox.). Opcionales de la Fase 1 no contratados: AAE 16.100 €, Landing Zone Advance 13.282 €, monitorización de certificados 1.610 €, workshop Intune 2.415 €, bolsa de 40 h 3.425 €.",
    "hitos": [
        H("2025-11-13", "Evaluación de proveedores: Labarit, Deloitte, Telefónica, Prodware (CAUs 145479, 145992, 146034, 146809)"),
        H("2025-12-04", "Propuesta Fase 1 de Prodware (OPP000529073)"),
        H("2026-01-13", "Inicio del assessment de unificación de tenants (CAU 149932)"),
        H("2026-03-11", "Propuesta Fase 2 (OPP000532115) y apertura del CAU 154991"),
        H("2026-04-05", "Assessment Fase 1 cerrado"),
        H("2026-12-06", "Fase 2: migración cross-tenant completada", hecho=False, aprox=True),
    ],
    "log": [
        {"fecha": "2026-11-03", "texto": "Cargadas las propuestas de Prodware: Fase 1 (3.220 €, realizada) y Fase 2 (28.405 €, en ejecución según CAU 154991). Confirmar aceptación formal y fechas reales de la Fase 2.", "estado": "En curso"},
    ],
}


def main():
    con = sqlite3.connect(DB_PATH)
    if con.execute("SELECT 1 FROM docs WHERE coll='proyectos' AND id=?", (PID,)).fetchone():
        print("El proyecto ya existe; no se toca."); return
    p = dict(PROYECTO); p["actualizado"] = datetime.now(timezone.utc).isoformat()
    con.execute("INSERT INTO docs VALUES ('proyectos',?,?)", (PID, json.dumps(p, ensure_ascii=False)))
    con.commit(); print("Proyecto Azure/Prodware creado: %d partidas (%.2f EUR), %d hitos." % (len(p["partidas"]), p["presupuesto"], len(p["hitos"])))


if __name__ == "__main__":
    main()
