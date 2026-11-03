#!/usr/bin/env python3
"""Actividad Seguridad IT — dashboard de proyectos e incidentes del área.

Lectura libre (sin login) para consulta; edición solo tras login con APP_PASSWORD.
Datos en SQLite (actividad.db) junto a este fichero. Sin dependencias más allá de Flask y python-dotenv.
"""
import csv
import io
import json
import os
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from clasificador import clasificar, severidad
from flask import Flask, Response, abort, jsonify, redirect, render_template_string, request, session, url_for

MAX_CSV_BYTES = 10 * 1024 * 1024

BASE = Path(__file__).resolve().parent
load_dotenv(BASE / ".env")

APP_PORT = int(os.getenv("APP_PORT", "8090"))
APP_PASSWORD = os.getenv("APP_PASSWORD", "")
APP_SECRET = os.getenv("APP_SECRET") or secrets.token_hex(32)
DB_PATH = BASE / os.getenv("DB_FILE", "actividad.db")
SEED_PATH = BASE / "seed.json"

if not APP_PASSWORD:
    raise SystemExit("Falta APP_PASSWORD en .env (contraseña del administrador)")

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = MAX_CSV_BYTES
app.secret_key = APP_SECRET
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")

DEF_CONFIG = {
    "departamento": "Departamento de IT · Seguridad de la Información",
    "titulo": "Actividad del área",
    "tipos": ["Phishing", "BEC / Fraude", "Malware", "Acceso no autorizado", "Fuga de datos",
              "Vulnerabilidad", "Disponibilidad", "Correo (SPF/DKIM/DMARC)", "Otro"],
}


# ---------------- almacenamiento ----------------
def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with db() as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS docs (
              coll TEXT NOT NULL, id TEXT NOT NULL, body TEXT NOT NULL,
              PRIMARY KEY (coll, id)
            );
            """
        )
        n = con.execute("SELECT COUNT(*) FROM docs").fetchone()[0]
    if n == 0 and SEED_PATH.exists():
        seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))
        with db() as con:
            con.execute("INSERT INTO docs VALUES ('config','general',?)", (json.dumps(seed.get("config", DEF_CONFIG), ensure_ascii=False),))
            for coll in ("proyectos", "incidentes"):
                for doc in seed.get(coll, []):
                    doc = dict(doc)
                    did = doc.pop("id")
                    con.execute("INSERT INTO docs VALUES (?,?,?)", (coll, did, json.dumps(doc, ensure_ascii=False)))


def get_all(coll):
    with db() as con:
        rows = con.execute("SELECT id, body FROM docs WHERE coll=?", (coll,)).fetchall()
    return [{"id": r["id"], **json.loads(r["body"])} for r in rows]


def get_config():
    with db() as con:
        r = con.execute("SELECT body FROM docs WHERE coll='config' AND id='general'").fetchone()
    return {**DEF_CONFIG, **(json.loads(r["body"]) if r else {})}


def put_doc(coll, did, body):
    with db() as con:
        con.execute("INSERT OR REPLACE INTO docs VALUES (?,?,?)", (coll, did, json.dumps(body, ensure_ascii=False)))


def del_doc(coll, did):
    with db() as con:
        con.execute("DELETE FROM docs WHERE coll=? AND id=?", (coll, did))


# ---------------- auth ----------------
def is_admin():
    return session.get("admin") is True


def require_admin():
    if not is_admin():
        abort(401)


LOGIN_HTML = """<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Entrar — Actividad Seguridad IT</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono&display=swap">
<style>html{color-scheme:dark}body{margin:0;min-height:100vh;display:grid;place-items:center;background:#121A2C;color:#E8ECF4;font-family:"IBM Plex Sans",system-ui,sans-serif}
form{background:#1A2439;border:1px solid #2B3853;border-radius:8px;padding:26px 28px;width:min(92vw,340px);display:grid;gap:12px}
.eyebrow{font-family:"IBM Plex Mono",monospace;font-size:.68rem;letter-spacing:.09em;text-transform:uppercase;color:#9AA6BF}
h1{margin:0;font-size:1.1rem;font-weight:600}input{font:inherit;background:#1E2A44;border:1px solid #2B3853;border-radius:6px;padding:9px;color:inherit}
button{font:inherit;background:#C49A2A;border:0;border-radius:6px;padding:9px;font-weight:600;color:#141414;cursor:pointer}
.err{color:#E0564F;font-size:.85rem}a{color:#9AA6BF;font-size:.8rem}</style></head><body>
<form method="post"><span class="eyebrow">SGP · Departamento de IT</span><h1>Administración del dashboard</h1>
<input type="password" name="password" placeholder="Contraseña" autofocus required>
{% if error %}<div class="err">Contraseña incorrecta.</div>{% endif %}
<button type="submit">Entrar</button><a href="{{ url_for('index') }}">← Volver al dashboard</a></form></body></html>"""


@app.route("/login", methods=["GET", "POST"])
def login():
    error = False
    if request.method == "POST":
        if secrets.compare_digest(request.form.get("password", ""), APP_PASSWORD):
            session["admin"] = True
            return redirect(url_for("index"))
        error = True
    return render_template_string(LOGIN_HTML, error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ---------------- páginas / API ----------------
_TEMPLATE = (BASE / "templates" / "index.html").read_text(encoding="utf-8")


@app.route("/")
def index():
    html = _TEMPLATE.replace("__IS_ADMIN__", "true" if is_admin() else "false")
    return Response(html, mimetype="text/html")


@app.route("/api/data")
def api_data():
    return jsonify({"config": get_config(), "proyectos": get_all("proyectos"), "incidentes": get_all("incidentes"),
                    "caus": get_all("caus")})


def _stamp(body):
    body = {k: v for k, v in dict(body).items() if k != "id"}
    body["actualizado"] = datetime.now(timezone.utc).isoformat()
    return body


def _check_id(did):
    if not did or len(did) > 64 or not all(c.isalnum() or c in "-_" for c in did):
        abort(400)


@app.route("/api/proyectos/<did>", methods=["PUT", "DELETE"])
def api_proyecto(did):
    require_admin()
    _check_id(did)
    if request.method == "DELETE":
        del_doc("proyectos", did)
        return jsonify(ok=True)
    body = request.get_json(silent=True) or {}
    if not str(body.get("nombre", "")).strip():
        abort(400)
    put_doc("proyectos", did, _stamp(body))
    return jsonify(ok=True)


@app.route("/api/incidentes/<did>", methods=["PUT", "DELETE"])
def api_incidente(did):
    require_admin()
    _check_id(did)
    if request.method == "DELETE":
        del_doc("incidentes", did)
        return jsonify(ok=True)
    body = request.get_json(silent=True) or {}
    if not body.get("fecha") or not str(body.get("titulo", "")).strip():
        abort(400)
    put_doc("incidentes", did, _stamp(body))
    return jsonify(ok=True)


@app.route("/api/config", methods=["PUT"])
def api_config():
    require_admin()
    body = request.get_json(silent=True) or {}
    cfg = {**get_config(), **{k: body[k] for k in ("departamento", "titulo", "tipos", "mitre") if k in body}}
    cfg["actualizado"] = datetime.now(timezone.utc).isoformat()
    put_doc("config", "general", cfg)
    return jsonify(ok=True)


# ---------------- CAUs (import CSV de ServiceDesk) ----------------
CAU_COLS = {
    "id de la solicitud": "id", "asunto": "asunto", "solicitante": "solicitante", "técnico": "tecnico",
    "tecnico": "tecnico", "fecha de vencimiento": "vencimiento", "estado": "estado", "fecha de creación": "creacion",
    "fecha de creacion": "creacion", "sitio": "sitio", "prioridad": "prioridad", "grupo": "grupo",
    "es solicitud de servicio": "servicio",
}


def _parse_sd_date(txt):
    """'03/11/2026 10:43 AM' -> '2026-11-03T10:43' (vacío si no se reconoce)."""
    txt = (txt or "").strip()
    for fmt in ("%d/%m/%Y %I:%M %p", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
        try:
            return datetime.strptime(txt, fmt).strftime("%Y-%m-%dT%H:%M")
        except ValueError:
            continue
    return ""


def parse_servicedesk_csv(raw: bytes):
    """Devuelve la lista de tickets del CSV exportado por ServiceDesk.
    Tolera las líneas de cabecera del informe (título, 'Generado por', 'Registros totales')."""
    text = None
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        raise ValueError("No se pudo leer el fichero (codificación desconocida)")
    rows = list(csv.reader(io.StringIO(text)))
    header_idx = next((i for i, r in enumerate(rows) if any("id de la solicitud" in (c or "").strip().lower() for c in r)), None)
    if header_idx is None:
        raise ValueError("No encuentro la columna 'ID de la solicitud' en el CSV")
    header = [CAU_COLS.get((c or "").strip().lower(), None) for c in rows[header_idx]]
    out = []
    for r in rows[header_idx + 1:]:
        if not r or not any((c or "").strip() for c in r):
            continue
        d = {}
        for key, val in zip(header, r):
            if key:
                d[key] = (val or "").strip()
        tid = d.get("id", "")
        if not tid.isdigit():
            continue
        d["estado"] = d.get("estado", "").upper()
        d["creacion"] = _parse_sd_date(d.get("creacion"))
        d["vencimiento"] = _parse_sd_date(d.get("vencimiento"))
        d["servicio"] = d.get("servicio", "").lower() == "true"
        out.append(d)
    return out


@app.route("/api/caus/import", methods=["POST"])
def api_caus_import():
    require_admin()
    f = request.files.get("file")
    if not f:
        return jsonify(error="Falta el fichero"), 400
    try:
        tickets = parse_servicedesk_csv(f.read())
    except ValueError as e:
        return jsonify(error=str(e)), 400
    existing = {t["id"] for t in get_all("caus")}
    inc_existing = {i["id"] for i in get_all("incidentes")}
    nuevos = actualizados = incidentes_nuevos = 0
    now = datetime.now(timezone.utc).isoformat()
    with db() as con:
        for t in tickets:
            tid = t.pop("id")
            t["actualizado"] = now
            tipo = clasificar(t.get("asunto", ""))
            t["tipo_incidente"] = tipo
            con.execute("INSERT OR REPLACE INTO docs VALUES ('caus',?,?)", (tid, json.dumps(t, ensure_ascii=False)))
            if tid in existing:
                actualizados += 1
            else:
                nuevos += 1
            # Incidente de seguridad derivado del CAU (solo se crea la primera vez; luego manda lo editado a mano)
            iid = "cau-" + tid
            if tipo and iid not in inc_existing and t.get("creacion"):
                inc = {
                    "fecha": t["creacion"][:10], "tipo": tipo, "severidad": severidad(t.get("asunto", ""), tipo),
                    "ref": "CAU " + tid, "titulo": t.get("asunto", ""),
                    "descripcion": "Solicitante: " + t.get("solicitante", "") + ". Clasificado automáticamente por el asunto del CAU.",
                    "estado": "Resuelto" if t.get("estado") == "CERRADA" else "Abierto",
                    "origen": "cau", "cau_id": tid, "auto": True, "aprox": False, "actualizado": now,
                }
                con.execute("INSERT INTO docs VALUES ('incidentes',?,?)", (iid, json.dumps(inc, ensure_ascii=False)))
                incidentes_nuevos += 1
    cfg = get_config()
    cfg["caus_import"] = now
    put_doc("config", "general", cfg)
    return jsonify(ok=True, importados=len(tickets), nuevos=nuevos, actualizados=actualizados, incidentes=incidentes_nuevos)


@app.route("/api/caus", methods=["DELETE"])
def api_caus_clear():
    require_admin()
    with db() as con:
        con.execute("DELETE FROM docs WHERE coll='caus'")
    return jsonify(ok=True)


@app.route("/api/export")
def api_export():
    """Copia de seguridad completa en JSON (solo administrador)."""
    require_admin()
    data = {"config": get_config(), "proyectos": get_all("proyectos"), "incidentes": get_all("incidentes"),
            "caus": get_all("caus")}
    return Response(json.dumps(data, ensure_ascii=False, indent=2), mimetype="application/json",
                    headers={"Content-Disposition": "attachment; filename=actividad-export.json"})


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=APP_PORT, debug=False)
