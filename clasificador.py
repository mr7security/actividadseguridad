"""Clasificación de asuntos de CAU como incidentes de seguridad.

Devuelve el tipo de incidente si el asunto apunta a uno, o None si es una petición ordinaria.
Las reglas son de palabras clave (sin acentos, minúsculas); el orden importa: la primera que encaja gana.
"""
import re
import unicodedata

REGLAS = [
    ("BEC / Fraude", [
        "estafa", "fraude", "bancari", "actualizar mis datos", "actualizacion bancaria", "pago", "factura", "invoice",
        "payroll", "cartera pendiente", "transferencia", "releve de compte", "aviso de vencimiento", "statement",
        "seguimiento de factura", "fac ", "#fac", "comunicacion envio",
    ]),
    ("Correo (SPF/DKIM/DMARC)", ["dmarc", "spf", "dkim", "error en correos enviados"]),
    ("Acceso no autorizado", [
        "contrasenas vulneradas", "contrasena vulnerada", "hackeo", "peligro de contrasena", "cuenta comprometida",
        "acceso no autorizado", "credenciales filtradas",
    ]),
    ("Malware", ["virus", "malware", "ransomware", "troyano"]),
    ("Vulnerabilidad", [
        "vulnerab", "actualizacion de seguridad", "no conformidades", "auditoria scan", "scan auditoria",
        "scan_c-pat", "parche",
    ]),
    ("Phishing", [
        "phishing", "physing", "phising", "sospechoso", "sospechosa", "suplantacion", "spam", "cuarentena",
        "correo no deseado", "no deseado", "aviso mensaje", "oauth", "sharepoint", "e-mail sospechoso",
        "correo revisar", "urgent product enquiry", "shared", "stocklogistic", "akkonlines",
    ]),
]

# Asuntos que, aunque contengan una palabra clave, no son incidentes
EXCLUIR = [
    "whatsapp", "whatsap", "wasap", "whastapp", "whatssap", "licencia", "chatgpt", "chat gpt", "copilot", "claude",
    "instalar", "instalacion", "permiso", "acceso a informacion", "accesos ", "gmao", "prueba", "proyecto",
    "jotform", "cuenta chatgpt", "cuenta nominal", "nominativ", "nominal", "encuesta", "certificado digital",
    "blanqueo de contrasena", "cambio nombre", "config", "d365", "dynamics", "terminal", "telefono", "cype",
    "mdm", "citrix", "octoparse", "access", "traductor", "pdf", "outlook", "calendario", "copia de web",
    "pagina web", "webs no van", "web stn", "app", "sms", "cargas", "assessment", "dependencias", "usuario",
    "integracion", "prodware", "azure", "deloitte", "telefonica", "labarit", "bot ", "idener", "api integration",
    "informe soporte", "consulta cliente", "certificacion de cliente", "seguridad y tecnologia",
    "ia e seguridad", "gmail", "lists", "portal cliente", "grupo castilla", "jaggaer", "silmeca",
    "informacion para certificacion", "propuesta de ciberseguridad", "seguimiento gmao", "modificacion informes",
    "upgrade", "wps office", "filtro de spam", "bloqueo sophos", "renovacion secreto", "jefes de turno",
]

# Un asunto reenviado (RV:/FW:/Fwd:) que no es una petición conocida casi siempre es un correo que el usuario
# manda a revisar por sospechoso: se clasifica como Phishing con severidad baja para que se revise.
REENVIO = re.compile(r"^(rv|fw|fwd|re)\s*:")


def _norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", s).strip()


def clasificar(asunto):
    a = _norm(asunto)
    if not a:
        return None
    # excepciones fuertes (lo que se parece a seguridad pero no lo es)
    for ex in EXCLUIR:
        if ex in a:
            # un asunto excluido solo cuenta si además tiene una señal inequívoca
            if not any(k in a for k in ("phishing", "physing", "estafa", "virus", "suplantacion", "hackeo", "vulnerad", "dmarc")):
                return None
            break
    for tipo, claves in REGLAS:
        if any(k in a for k in claves):
            return tipo
    if REENVIO.match(a) and not any(ex in a for ex in EXCLUIR):
        return "Phishing"
    return None


def severidad(asunto, tipo):
    a = _norm(asunto)
    if tipo in ("BEC / Fraude", "Acceso no autorizado") or "estafa" in a or "hackeo" in a or "vulnerad" in a:
        return "Alta"
    if REENVIO.match(a) and not any(k in a for k in ("phishing", "physing", "virus", "sospech", "suplant", "spam", "cuarentena")):
        return "Baja"
    return "Media"
