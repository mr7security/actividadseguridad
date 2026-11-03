#!/usr/bin/env python3
"""Seguimiento de la Fase 2 del proyecto Azure/Prodware (bloqueos y estado a 03/11/2026). Idempotente."""
import json, os, sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / os.getenv("DB_FILE", "actividad.db")
PID = "p-azure-prodware"

LOG = [
    {"fecha": "2026-03-11", "texto": "Inicio de la Fase 2 (ejecución de la unificación) con la apertura del CAU 154991.", "estado": "En curso"},
    {"fecha": "2026-06-15", "texto": "Bloqueo por cambio del equipo de cuentas de Prodware: sale Miguel Pastor (Account Manager) y no asignan PO nuevo; José Blanco toma el tema. Unos 15 días perdidos. (Fecha aprox.)", "estado": "En pausa"},
    {"fecha": "2026-08-15", "texto": "Problemas con el técnico para organizar el nuevo plan de recursos de OK Ticket: 10 días más de retraso. (Fecha aprox.)", "estado": "En curso"},
    {"fecha": "2026-09-07", "texto": "Replanificación del proyecto (primera semana de septiembre).", "estado": "En curso"},
    {"fecha": "2026-09-21", "texto": "El técnico asignado deja Prodware; nuevo técnico asignado, 15 días más perdidos mientras entra en el tema. (Fecha aprox.)", "estado": "En pausa"},
    {"fecha": "2026-11-03", "texto": "En ejecución: despliegue de los recursos de STN en el tenant de Serviplana.", "estado": "En curso"},
]
HITOS = [
    {"fecha": "2026-06-15", "nombre": "Bloqueo: cambio del equipo de cuentas de Prodware (~15 días)", "hecho": True, "aprox": True},
    {"fecha": "2026-08-15", "nombre": "Retraso: plan de recursos de OK Ticket (~10 días)", "hecho": True, "aprox": True},
    {"fecha": "2026-09-07", "nombre": "Replanificación de la Fase 2", "hecho": True, "aprox": True},
    {"fecha": "2026-09-21", "nombre": "Cambio de técnico de Prodware (~15 días)", "hecho": True, "aprox": True},
    {"fecha": "2026-11-03", "nombre": "Despliegue de recursos de STN en Serviplana en curso", "hecho": True, "aprox": False},
]


def main():
    con = sqlite3.connect(DB_PATH)
    row = con.execute("SELECT body FROM docs WHERE coll='proyectos' AND id=?", (PID,)).fetchone()
    if not row:
        print("No existe el proyecto; ejecuta antes cargar_azure_prodware.py"); return
    p = json.loads(row[0])
    tx = {e.get("texto") for e in p.get("log", [])}; nl = [e for e in LOG if e["texto"] not in tx]
    nm = {h.get("nombre") for h in p.get("hitos", [])}; nh = [h for h in HITOS if h["nombre"] not in nm]
    if not nl and not nh:
        print("Seguimiento ya cargado; no se toca."); return
    # quitar la nota genérica de la alta, ya sustituida por el seguimiento real
    p["log"] = [e for e in p.get("log", []) if not e.get("texto", "").startswith("Cargadas las propuestas de Prodware")] + nl
    p["hitos"] = p.get("hitos", []) + nh
    p["estado"] = "En curso"; p["avance"] = 60
    p["notas"] = ("Importes sin IVA. Fase 2 factura 20 % a la firma, 60 % por avance mensual y 20 % al cierre. "
                  "Retraso acumulado en la Fase 2 de unos 40 días por cambios de equipo en Prodware (cuentas y técnico) y por el plan de recursos de OK Ticket. "
                  "Fecha de fin estimada (aprox.). Opcionales de la Fase 1 no contratados: AAE 16.100 €, Landing Zone Advance 13.282 €, monitorización de certificados 1.610 €, workshop Intune 2.415 €, bolsa de 40 h 3.425 €.")
    p["actualizado"] = datetime.now(timezone.utc).isoformat()
    con.execute("UPDATE docs SET body=? WHERE coll='proyectos' AND id=?", (json.dumps(p, ensure_ascii=False), PID))
    con.commit(); print("Listo: %d notas y %d hitos añadidos; avance 60 %%." % (len(nl), len(nh)))


if __name__ == "__main__":
    main()
