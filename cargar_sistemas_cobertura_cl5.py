#!/usr/bin/env python3
"""Fusiona 'Mejoras Wi-Fi CL5' dentro de 'Estudios de cobertura' como sub-puntos de la actuación 'Mejoras CL5',
fija el inicio en octubre de 2026 y elimina el proyecto independiente. Idempotente."""
import json, os, sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / os.getenv("DB_FILE", "actividad.db")
PID, OLD = "p-sis-cobertura", "p-sis-mejoras-cl5"
A = lambda n, v=0, sub=False: {"nombre": n, "avance": v, "sub": sub}
ACTUACIONES = [
    A("Estudios", 100), A("Revisar informes", 14), A("Mejoras CL5", 35),
    A("Ajuste de potencias de los puntos de acceso", 100, True), A("Aumento de la velocidad mínima en ambas bandas", 100, True),
    A("Solicitud a Multicode para añadir los nuevos canales a las carretillas", 100, True), A("Ampliación de canales de 5 GHz", 50, True),
    A("Habilitar nuevos canales en terminales", 50, True), A("Habilitarlos en el controlador Wi-Fi y eliminar la configuración manual", 50, True),
    A("Retirar Wi-Fi logística de los AP de oficinas", 0, True), A("Eliminar Wi-Fi logística-5 GHz y migrar dispositivos a SGP-logística", 0, True),
    A("Bajar los AP direccionales de Nave Inteligente", 0, True), A("Cambiar soporte del AP omnidireccional", 0, True), A("Sustituir AP averiado", 0, True),
    A("Revisar y apagar Cisco", 0, True), A("Revisar Moxa y el tráfico de vídeo", 0, True),
]


def main():
    con = sqlite3.connect(DB_PATH); now = datetime.now(timezone.utc).isoformat()
    row = con.execute("SELECT body FROM docs WHERE coll='proyectos' AND id=?", (PID,)).fetchone()
    if not row:
        print("No existe Estudios de cobertura; ejecuta antes cargar_sistemas_cobertura.py"); return
    p = json.loads(row[0]); ch = False
    if p.get("actuaciones") != ACTUACIONES:
        p["actuaciones"] = ACTUACIONES; ch = True
    if p.get("inicio") != "2026-10-01":
        p["inicio"] = "2026-10-01"; p["notas"] = (p.get("notas") or "").replace(" Fecha de inicio aproximada (01/01/2026).", "").strip(); ch = True
    if con.execute("SELECT 1 FROM docs WHERE coll='proyectos' AND id=?", (OLD,)).fetchone():
        con.execute("DELETE FROM docs WHERE coll='proyectos' AND id=?", (OLD,)); print("Eliminado el proyecto independiente Mejoras Wi-Fi CL5."); ch = True
    if ch:
        p["avance"] = 50; p["actualizado"] = now
        p.setdefault("log", []).append({"fecha": "2026-11-25", "texto": "Las 13 mejoras de CL5 pasan a ser sub-puntos de la actuación 'Mejoras CL5'. Inicio del proyecto: octubre de 2026.", "estado": p.get("estado", "En curso")})
        con.execute("UPDATE docs SET body=? WHERE coll='proyectos' AND id=?", (json.dumps(p, ensure_ascii=False), PID)); con.commit(); print("Estudios de cobertura actualizado.")
    else:
        print("Ya estaba al día; no se toca.")


if __name__ == "__main__":
    main()
