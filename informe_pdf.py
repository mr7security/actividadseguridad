"""Informe PDF de proyectos (reportlab). Usado por /api/proyectos.pdf."""
import io
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (CondPageBreak, Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle)

NAVY = colors.HexColor("#1E2A44"); GOLD = colors.HexColor("#C49A2A"); GREY = colors.HexColor("#5B6782")
LINE = colors.HexColor("#D6DCE8"); PANEL = colors.HexColor("#F3F5F9"); INFO = colors.HexColor("#2D6BC4")
OK = colors.HexColor("#1F8F5F"); WARN = colors.HexColor("#B57B12"); BAD = colors.HexColor("#C23B35")
AREAS = {"seg": "Seguridad de la Información", "sis": "Sistemas e Infraestructura"}
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
LOGO = Path(__file__).resolve().parent / "assets" / "sgp.png"

ss = getSampleStyleSheet()
H1 = ParagraphStyle("h1", parent=ss["Title"], fontName="Helvetica-Bold", fontSize=16, textColor=NAVY, alignment=0, spaceAfter=0, spaceBefore=0)
H2 = ParagraphStyle("h2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=11.5, textColor=NAVY, spaceBefore=4, spaceAfter=2)
H3 = ParagraphStyle("h3", parent=ss["Heading3"], fontName="Helvetica-Bold", fontSize=8.5, textColor=GREY, spaceBefore=4, spaceAfter=1)
EYE = ParagraphStyle("eye", fontName="Helvetica", fontSize=7.5, textColor=GREY, leading=9)
BODY = ParagraphStyle("body", fontName="Helvetica", fontSize=8.8, leading=11, textColor=colors.HexColor("#1A2235"))
SMALL = ParagraphStyle("small", parent=BODY, fontSize=8, leading=10, textColor=GREY)
CELL = ParagraphStyle("cell", parent=BODY, fontSize=8.2, leading=10)
CELLR = ParagraphStyle("cellr", parent=CELL, alignment=TA_RIGHT)


def fmt_d(s):
    if not s:
        return "—"
    s = str(s)[:10]
    try:
        y, m, d = s.split("-"); return f"{d}/{m}/{y}"
    except ValueError:
        return s


def eur(v):
    try:
        return f"{float(v):,.0f} €".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return "—"


def act_tree(p):
    out = []
    for x in (p.get("actuaciones") or []):
        if not x.get("nombre"):
            continue
        if x.get("sub") and out:
            out[-1]["subs"].append({"nombre": x["nombre"], "avance": float(x.get("avance") or 0)})
        else:
            out.append({"nombre": x["nombre"], "avance": float(x.get("avance") or 0), "subs": []})
    for a in out:
        if a["subs"]:
            a["avance"] = round(sum(y["avance"] for y in a["subs"]) / len(a["subs"]))
    return out


def avance(p):
    acts = act_tree(p)
    if acts:
        return round(sum(a["avance"] for a in acts) / len(acts))
    return max(0, min(100, int(float(p.get("avance") or 0))))


def pres(p):
    part = [x for x in (p.get("partidas") or []) if x.get("precio") is not None]
    if part:
        return sum(float(x.get("unidades") or 0) * float(x.get("precio") or 0) for x in part)
    v = p.get("presupuesto")
    return float(v) if v not in (None, "") else None


def bar(pct, w=60 * mm, h=3.2 * mm, color=INFO):
    pct = max(0, min(100, pct))
    t = Table([["", ""]], colWidths=[w * pct / 100 if pct else 0.01, w * (100 - pct) / 100 if pct < 100 else 0.01], rowHeights=[h])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), color), ("BACKGROUND", (1, 0), (1, 0), LINE),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                           ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    return t


def estado_color(e):
    return {"Finalizado": OK, "En pausa": WARN, "Planificado": GREY}.get(e, INFO)


def kpi_table(items):
    cells = []
    for lbl, val, sub in items:
        cells.append([Paragraph(lbl.upper(), EYE), Paragraph(f"<font size=15><b>{val}</b></font>", BODY), Paragraph(sub, SMALL)])
    data = [[c[0] for c in cells], [c[1] for c in cells], [c[2] for c in cells]]
    t = Table(data, colWidths=[(A4[0] - 28 * mm) / len(items)] * len(items))
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PANEL), ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                           ("LINEAFTER", (0, 0), (-2, -1), 0.5, LINE), ("LEFTPADDING", (0, 0), (-1, -1), 8),
                           ("TOPPADDING", (0, 0), (-1, 0), 4), ("BOTTOMPADDING", (0, -1), (-1, -1), 4), ("TOPPADDING", (0, 1), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -2), 1)]))
    return t


def gantt(proyectos, year, width):
    """Línea temporal simplificada: una fila por proyecto, barra inicio→fin dentro del año."""
    from reportlab.graphics.shapes import Drawing, Line, Rect, String
    rows = []
    for p in proyectos:
        if p.get("estado") == "Finalizado" and not (p.get("inicio") or p.get("fin")):
            continue
        a = p.get("inicio") or f"{year}-01-01"; b = p.get("fin") or (date.today().isoformat() if p.get("estado") != "Finalizado" else a)
        if b < f"{year}-01-01" or a > f"{year}-12-31":
            continue
        rows.append((p, a, b))
    if not rows:
        return None
    L, R, rowH, top = 62 * mm, 12 * mm, 5.4 * mm, 7 * mm
    H = top + rowH * len(rows) + 2 * mm
    d = Drawing(width, H)
    y0 = date(year, 1, 1).toordinal(); span = date(year + 1, 1, 1).toordinal() - y0

    def sx(iso):
        try:
            o = date.fromisoformat(iso[:10]).toordinal()
        except ValueError:
            o = y0
        return L + (max(y0, min(o, y0 + span)) - y0) / span * (width - L - R)
    for i, m in enumerate(MESES):
        x1, x2 = sx(f"{year}-{i+1:02d}-01"), sx(f"{year}-{i+2:02d}-01") if i < 11 else width - R
        if i % 2:
            d.add(Rect(x1, 0, x2 - x1, H - top + 2 * mm, fillColor=colors.HexColor("#F3F5F9"), strokeColor=None))
        d.add(String((x1 + x2) / 2, H - top + 3 * mm, m, fontName="Helvetica", fontSize=6.5, fillColor=GREY, textAnchor="middle"))
    hoy = date.today()
    if hoy.year == year:
        x = sx(hoy.isoformat()); d.add(Line(x, 0, x, H - top + 2 * mm, strokeColor=GOLD, strokeWidth=0.8, strokeDashArray=[2, 2]))
    for i, (p, a, b) in enumerate(rows):
        y = H - top - (i + 1) * rowH + 1.5 * mm
        name = p.get("nombre", "")
        name = name if len(name) <= 42 else name[:41] + "…"
        d.add(String(L - 3 * mm, y + 0.6 * mm, name, fontName="Helvetica", fontSize=7, fillColor=colors.HexColor("#1A2235"), textAnchor="end"))
        x1, x2 = sx(a), max(sx(b), sx(a) + 1.5)
        col = estado_color(p.get("estado")); av = avance(p)
        d.add(Rect(x1, y, x2 - x1, 3.2 * mm, fillColor=colors.Color(col.red, col.green, col.blue, alpha=0.3), strokeColor=None))
        d.add(Rect(x1, y, (x2 - x1) * (100 if p.get("estado") == "Finalizado" else av) / 100, 3.2 * mm, fillColor=col, strokeColor=None))
        d.add(String(x2 + 1.5 * mm, y + 0.6 * mm, "✓" if p.get("estado") == "Finalizado" else f"{av} %", fontName="Helvetica", fontSize=6.5, fillColor=GREY))
        for h in p.get("hitos") or []:
            if h.get("fecha") and str(h["fecha"]).startswith(str(year)):
                x = sx(h["fecha"]); d.add(Rect(x - 1.2 * mm, y - 0.4 * mm, 2.4 * mm, 2.4 * mm, fillColor=col if h.get("hecho") else colors.white, strokeColor=NAVY, strokeWidth=0.5))
    return d


def proyecto_block(p, width):
    out = []
    est = p.get("estado", "—"); av = avance(p)
    head = Table([[Paragraph(f"<b>{p.get('nombre','')}</b>", ParagraphStyle("pn", parent=BODY, fontSize=11.5, leading=14, textColor=NAVY)),
                   Paragraph(f"<font color='{estado_color(est).hexval()}'><b>{est.upper()}</b></font>", ParagraphStyle("pe", parent=CELLR, fontSize=8))]],
                 colWidths=[width - 35 * mm, 35 * mm])
    head.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, 0), 0.8, GOLD), ("BOTTOMPADDING", (0, 0), (-1, -1), 2), ("TOPPADDING", (0, 0), (-1, -1), 0), ("LEFTPADDING", (0, 0), (0, 0), 0)]))
    out.append(head)
    if p.get("descripcion"):
        out.append(Paragraph(p["descripcion"], BODY))
    pv = pres(p)
    meta = [[Paragraph("AVANCE", EYE), Paragraph("MODALIDAD", EYE), Paragraph("INICIO", EYE), Paragraph("FIN", EYE), Paragraph("PRESUPUESTO", EYE), Paragraph("RECURSOS / PROVEEDOR", EYE)],
            [Table([[bar(av, 28 * mm), Paragraph(f"<b>{av} %</b>", CELL)]], colWidths=[29 * mm, 12 * mm], style=[("LEFTPADDING", (0, 0), (-1, -1), 0), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]),
             Paragraph(p.get("modalidad", "Interno"), CELL), Paragraph(fmt_d(p.get("inicio")), CELL), Paragraph(fmt_d(p.get("fin")), CELL),
             Paragraph(eur(pv) if pv is not None else "Sin presupuesto", CELL),
             Paragraph((("Proveedor: " + p["proveedor"]) if p.get("modalidad") == "Tercerizado" and p.get("proveedor") else (p.get("recursos") or "Recursos propios")), CELL)]]
    t = Table(meta, colWidths=[44 * mm, 22 * mm, 20 * mm, 20 * mm, 26 * mm, width - 132 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PANEL), ("LEFTPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, 0), 3), ("BOTTOMPADDING", (0, 0), (-1, 0), 0), ("TOPPADDING", (0, 1), (-1, 1), 1), ("BOTTOMPADDING", (0, 1), (-1, 1), 3), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    out.append(Spacer(1, 2)); out.append(t)
    acts = act_tree(p)
    if acts:
        SUB = ParagraphStyle("sub", parent=CELL, fontSize=7.6, leading=9, textColor=GREY, leftIndent=10)
        rows, subrows = [], []
        for a in acts:
            rows.append([Paragraph(f"<b>{a['nombre']}</b>" if a["subs"] else a["nombre"], CELL), bar(a["avance"], 50 * mm, color=OK if a["avance"] >= 100 else INFO), Paragraph(f"{int(a['avance'])} %", CELLR)])
            for y in a["subs"]:
                subrows.append(len(rows))
                rows.append([Paragraph("↳ " + y["nombre"], SUB), bar(y["avance"], 40 * mm, h=2.2 * mm, color=OK if y["avance"] >= 100 else INFO), Paragraph(f"{int(y['avance'])} %", ParagraphStyle("subr", parent=SUB, alignment=TA_RIGHT, leftIndent=0))])
        ta = Table(rows, colWidths=[width - 68 * mm, 52 * mm, 16 * mm]); st = [("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LINEBELOW", (0, 0), (-1, -1), 0.3, LINE), ("LEFTPADDING", (0, 0), (0, -1), 0)]
        for i in subrows:
            st += [("TOPPADDING", (0, i), (-1, i), 1), ("BOTTOMPADDING", (0, i), (-1, i), 1)]
        ta.setStyle(TableStyle(st))
        out.append(KeepTogether([Paragraph("Actuaciones", H3), ta]))
    part = [x for x in (p.get("partidas") or []) if x.get("concepto")]
    if part:
        rows = [[Paragraph(x["concepto"], CELL), Paragraph(f"{x.get('unidades',0)} × {eur(x.get('precio'))}" + (f" / {x['periodo']}" if x.get("periodo") else ""), CELLR), Paragraph(eur(float(x.get("unidades") or 0) * float(x.get("precio") or 0)), CELLR)] for x in part]
        rows.append([Paragraph("<b>Total</b>", CELL), "", Paragraph(f"<b>{eur(pv)}</b>", CELLR)])
        tp = Table(rows, colWidths=[width - 80 * mm, 48 * mm, 32 * mm]); tp.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -2), 0.3, LINE), ("LINEABOVE", (0, -1), (-1, -1), 0.8, NAVY), ("LEFTPADDING", (0, 0), (0, -1), 0)]))
        out.append(KeepTogether([Paragraph("Partidas de coste (sin impuestos)", H3), tp]))
    hitos = sorted([h for h in (p.get("hitos") or []) if h.get("fecha")], key=lambda h: h["fecha"])
    if hitos:
        rows = [[Paragraph(("<font name='ZapfDingbats'>4</font>" if h.get("hecho") else "<font name='ZapfDingbats'>m</font>"), ParagraphStyle("hk", parent=CELL, textColor=OK if h.get("hecho") else GREY)), Paragraph(fmt_d(h["fecha"]) + (" ~" if h.get("aprox") else ""), CELL), Paragraph(h.get("nombre", ""), CELL)] for h in hitos]
        th = Table(rows, colWidths=[6 * mm, 22 * mm, width - 28 * mm]); th.setStyle(TableStyle([("LEFTPADDING", (0, 0), (0, -1), 0), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
        out.append(KeepTogether([Paragraph("Hitos", H3), th]))
    log = sorted([e for e in (p.get("log") or []) if e.get("texto")], key=lambda e: e.get("fecha", ""), reverse=True)
    if p.get("estado") == "En pausa" and log:
        last = next((e for e in log if e.get("estado") == "En pausa"), log[0])
        out.append(Paragraph(f"<font color='{WARN.hexval()}'><b>En pausa desde {fmt_d(last.get('fecha'))}:</b> {last.get('texto','')}</font>", BODY))
    if log:
        rows = [[Paragraph(fmt_d(e.get("fecha")), SMALL), Paragraph(e.get("texto", ""), CELL)] for e in log[:4]]
        tl = Table(rows, colWidths=[22 * mm, width - 22 * mm]); tl.setStyle(TableStyle([("LEFTPADDING", (0, 0), (0, -1), 0), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
        out.append(KeepTogether([Paragraph("Registro de seguimiento", H3), tl]))
    if p.get("notas"):
        out.append(Paragraph(f"<i>{p['notas']}</i>", SMALL))
    out.append(Spacer(1, 6))
    return out


def build_pdf(proyectos, area, titulo, year=None, responsable=""):
    year = year or date.today().year
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm, topMargin=11 * mm, bottomMargin=14 * mm,
                            title=f"Informe de proyectos — {AREAS.get(area, area)}", author=responsable or "Departamento de IT · SGP")
    W = A4[0] - 28 * mm
    area_nombre = AREAS.get(area, area)
    hoy = date.today().strftime("%d/%m/%Y")

    def on_page(canvas, doc_):
        canvas.saveState(); canvas.setFont("Helvetica", 7.5); canvas.setFillColor(GREY)
        canvas.drawString(14 * mm, 8 * mm, f"SGP — Departamento de IT · {area_nombre}" + (f" · {responsable}" if responsable else "") + f" · {hoy}")
        canvas.drawRightString(A4[0] - 14 * mm, 8 * mm, f"Página {doc_.page}")
        canvas.setStrokeColor(LINE); canvas.line(14 * mm, 10.5 * mm, A4[0] - 14 * mm, 10.5 * mm); canvas.restoreState()

    story = []
    logo = Image(str(LOGO), width=30 * mm, height=30 * mm * 0.53) if LOGO.exists() else Spacer(1, 1)
    hdr = Table([[logo, [Paragraph("DEPARTAMENTO DE IT · " + area_nombre.upper(), EYE), Paragraph(titulo or "Informe de proyectos", H1), Paragraph((f"Responsable: {responsable} · " if responsable else "") + f"Estado a {hoy}", SMALL)]]], colWidths=[36 * mm, W - 36 * mm])
    hdr.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (0, 0), 0), ("LINEBELOW", (0, 0), (-1, 0), 1, NAVY), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story += [hdr, Spacer(1, 5)]

    en_curso = [p for p in proyectos if p.get("estado") == "En curso"]
    tot = sum(v for v in (pres(p) for p in proyectos) if v is not None)
    avg = round(sum(avance(p) for p in en_curso) / len(en_curso)) if en_curso else 0
    n_ext = len([p for p in proyectos if p.get("modalidad") == "Tercerizado"])
    story += [kpi_table([("Proyectos en curso", str(len(en_curso)), f"de {len(proyectos)} registrados"),
                         ("Avance medio", f"{avg} %", "proyectos en curso"),
                         ("Presupuesto", eur(tot) if tot else "0 €", f"{len([p for p in proyectos if pres(p) is not None])} proyectos con presupuesto"),
                         ("Internos / tercerizados", f"{len(proyectos) - n_ext} / {n_ext}", "en total")]), Spacer(1, 6)]

    order = {"En curso": 0, "En pausa": 1, "Planificado": 2, "Finalizado": 3}
    ordenados = sorted(proyectos, key=lambda p: (order.get(p.get("estado"), 9), -(avance(p))))
    story.append(Paragraph("Resumen", H2))
    rows = [[Paragraph("<b>Proyecto</b>", CELL), Paragraph("<b>Modalidad</b>", CELL), Paragraph("<b>Estado</b>", CELL), Paragraph("<b>Avance</b>", CELLR), Paragraph("<b>Inicio</b>", CELL), Paragraph("<b>Fin</b>", CELL), Paragraph("<b>Presupuesto</b>", CELLR)]]
    for p in ordenados:
        pv = pres(p)
        rows.append([Paragraph(p.get("nombre", ""), CELL), Paragraph(p.get("modalidad", "Interno"), CELL),
                     Paragraph(f"<font color='{estado_color(p.get('estado')).hexval()}'>{p.get('estado','')}</font>", CELL),
                     Paragraph(f"{avance(p)} %", CELLR), Paragraph(fmt_d(p.get("inicio")), CELL), Paragraph(fmt_d(p.get("fin")), CELL), Paragraph(eur(pv) if pv is not None else "—", CELLR)])
    tr = Table(rows, colWidths=[W - 124 * mm, 22 * mm, 20 * mm, 16 * mm, 20 * mm, 20 * mm, 26 * mm], repeatRows=1)
    tr.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), PANEL), ("LINEBELOW", (0, 0), (-1, 0), 0.8, NAVY), ("LINEBELOW", (0, 1), (-1, -1), 0.3, LINE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (0, -1), 2)]))
    story += [tr, Spacer(1, 4)]

    g = gantt(ordenados, year, W)
    if g:
        story += [Paragraph(f"Línea temporal {year}", H2), g, Paragraph("Barra: inicio → fin (relleno = avance) · cuadrado relleno = hito cumplido, vacío = pendiente · línea punteada = hoy", SMALL), Spacer(1, 3)]

    for titulo_g, lista in (("Proyectos tercerizados", [p for p in ordenados if p.get("modalidad") == "Tercerizado"]),
                            ("Proyectos internos", [p for p in ordenados if p.get("modalidad") != "Tercerizado"])):
        if not lista:
            continue
        story += [Spacer(1, 4), Paragraph(titulo_g, H2)]
        for p in lista:
            blk = proyecto_block(p, W)
            # Altura de la ficha: si no cabe en lo que queda de página, pasa entera a la siguiente;
            # si es más alta que una página, se parte solo entre secciones (cada una va en KeepTogether).
            avail_h = A4[1] - 25 * mm
            def alto(f):
                if isinstance(f, KeepTogether):
                    return sum(alto(x) for x in f._content)
                try:
                    return f.wrap(W, avail_h)[1] + getattr(f, "spaceBefore", 0) + getattr(f, "spaceAfter", 0)
                except Exception:
                    return 0
            h = sum(alto(f) for f in blk)
            story.append(CondPageBreak(min(h, avail_h * 0.95)))
            story.append(KeepTogether(blk[:4]))
            story += blk[4:]
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    return buf.getvalue()
