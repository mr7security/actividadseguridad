#!/usr/bin/env python3
"""Alta/actualización única del proyecto 'Mejoras Wi-Fi CL5' (Sistemas e Infraestructura) con sus actuaciones."""
import json, os, sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / os.getenv("DB_FILE", "actividad.db")
PID = "p-sis-mejoras-cl5"
A = lambda n, v=0: {"nombre": n, "avance": v}
PROYECTO = {
    "area": "sis", "nombre": "Mejoras Wi-Fi CL5",
    "descripcion": "Plan de mejoras de la red inalámbrica del Centro Logístico 5 derivado del estudio de cobertura: potencias y velocidades mínimas de los AP, ampliación de canales de 5 GHz en controlador, terminales y carretillas (Multicode), limpieza de SSID de logística, recolocación y sustitución de AP, y revisión de equipos Cisco y Moxa.",
    "modalidad": "Interno", "proveedor": "", "estado": "En curso", "avance": 35,
    "inicio": "", "fin": "", "moneda": "EUR", "presupuesto": None, "partidas": [], "recursos": "Sistemas e Infraestructura · Multicode (carretillas)",
    "actuaciones": [
        A("Ajuste de potencias de los puntos de acceso", 100),
        A("Aumento de la velocidad mínima en ambas bandas", 100),
        A("Solicitud a Multicode para añadir los nuevos canales a las carretillas", 100),
        A("Ampliación de canales de 5 GHz", 50),
        A("Habilitar nuevos canales en terminales", 50),
        A("Habilitarlos en el controlador Wi-Fi y eliminar la configuración manual", 50),
        A("Retirar Wi-Fi logística de los AP de oficinas"),
        A("Eliminar Wi-Fi logística-5 GHz y migrar dispositivos a SGP-logística"),
        A("Bajar los AP direccionales de Nave Inteligente"),
        A("Cambiar soporte del AP omnidireccional"),
        A("Sustituir AP averiado"),
        A("Revisar y apagar Cisco"),
        A("Revisar Moxa y el tráfico de vídeo"),
    ],
    "hitos": [],
    "log": [{"fecha": "2026-11-25", "texto": "Estado: potencias, velocidades mínimas y solicitud a Multicode completadas; canales de 5 GHz en controlador y terminales al 50 %; resto pendiente. Es la actuación 'Mejoras CL5' del proyecto Estudios de cobertura.", "estado": "En curso"}],
    "notas": "Relacionado con 'Estudios de cobertura' (actuación Mejoras CL5). Pendiente: fechas y coste de los AP a sustituir.",
}


def main():
    con = sqlite3.connect(DB_PATH)
    now = datetime.now(timezone.utc).isoformat()
    row = con.execute("SELECT body FROM docs WHERE coll='proyectos' AND id=?", (PID,)).fetchone()
    if row:
        p = json.loads(row[0])
        if p.get("actuaciones") == PROYECTO["actuaciones"]:
            print("El proyecto ya está al día; no se toca."); return
        p["actuaciones"] = PROYECTO["actuaciones"]; p["avance"] = PROYECTO["avance"]; p["actualizado"] = now
        con.execute("UPDATE docs SET body=? WHERE coll='proyectos' AND id=?", (json.dumps(p, ensure_ascii=False), PID)); con.commit()
        print("Actualizado:", p["nombre"]); return
    p = dict(PROYECTO); p["actualizado"] = now
    con.execute("INSERT INTO docs VALUES ('proyectos',?,?)", (PID, json.dumps(p, ensure_ascii=False))); con.commit()
    print("Creado:", p["nombre"], "con", len(p["actuaciones"]), "actuaciones.")


if __name__ == "__main__":
    main()
