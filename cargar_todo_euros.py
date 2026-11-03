#!/usr/bin/env python3
"""Pasa a euros las partidas en dólares (ChatGPT Business: 240 $ → 220,80 €, 1.200 $ → 1.104 €) y fija todos los proyectos en EUR. Idempotente."""
import json, os, sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / os.getenv("DB_FILE", "actividad.db")
RATE = 0.92


def main():
    con = sqlite3.connect(DB_PATH)
    n = 0
    for pid, body in con.execute("SELECT id, body FROM docs WHERE coll='proyectos'").fetchall():
        p = json.loads(body); ch = False
        pm = p.get("moneda", "EUR")
        for x in p.get("partidas", []):
            cm = x.get("moneda") or pm
            if cm == "USD":
                x["precio"] = round(float(x.get("precio") or 0) * RATE, 2); x["concepto"] = x.get("concepto", "").replace("US$", "€").replace("$", "€"); ch = True
            if x.get("moneda") != "EUR":
                x["moneda"] = "EUR"; ch = True
        if pm != "EUR":
            if not p.get("partidas") and p.get("presupuesto") not in (None, ""):
                p["presupuesto"] = round(float(p["presupuesto"]) * RATE, 2)
            p["moneda"] = "EUR"; ch = True
        if p.get("partidas"):
            tot = round(sum((x.get("precio") or 0) * (x.get("unidades") or 0) for x in p["partidas"]), 2)
            if p.get("presupuesto") != tot:
                p["presupuesto"] = tot; ch = True
        if ch:
            p["actualizado"] = datetime.now(timezone.utc).isoformat()
            con.execute("UPDATE docs SET body=? WHERE coll='proyectos' AND id=?", (json.dumps(p, ensure_ascii=False), pid)); n += 1
    con.commit(); print("Proyectos actualizados:", n)


if __name__ == "__main__":
    main()
