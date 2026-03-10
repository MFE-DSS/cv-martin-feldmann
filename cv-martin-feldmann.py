#!/usr/bin/env python3
"""
Génère Martin_Feldmann_CV.pdf dans un dossier configurable.

Usage
-----
  python3 cv-martin-feldmann.py                          # → ~/Desktop/CV/
  python3 cv-martin-feldmann.py --output-dir /tmp/cv     # dossier explicite
  CV_OUTPUT_DIR=/tmp/cv python3 cv-martin-feldmann.py    # via env var

Dépendances
-----------
  pip install reportlab
"""
import argparse
import os
import platform

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether, Flowable, ListFlowable, ListItem,
    Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)


# ── CLI / Env ────────────────────────────────────────────────────────────────
def _default_output_dir() -> str:
    """Détecte automatiquement le bon dossier de sortie selon l'environnement.

    Priorité :
    1. $CV_OUTPUT_DIR  (variable d'env explicite)
    2. ./output        (CI : GitHub Actions, GitLab CI, etc.)
    3. ~/Desktop/CV    (usage local macOS / Windows / Linux)
    """
    if os.environ.get("CV_OUTPUT_DIR"):
        return os.environ["CV_OUTPUT_DIR"]
    if os.environ.get("CI"):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    return os.path.join(os.path.expanduser("~"), "Desktop", "CV")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Génère le CV de Martin Feldmann en PDF.")
    p.add_argument(
        "--output-dir", "-o",
        default=_default_output_dir(),
        help="Dossier de destination du PDF (défaut : ~/Desktop/CV ou $CV_OUTPUT_DIR)",
    )
    p.add_argument(
        "--filename", "-f",
        default="Martin_Feldmann_CV.pdf",
        help="Nom du fichier PDF (défaut : Martin_Feldmann_CV.pdf)",
    )
    return p.parse_args()


# ── Polices ──────────────────────────────────────────────────────────────────
_FONT_CANDIDATES = {
    "DejaVuSans": [
        # macOS (avec DejaVu installé)
        "/Library/Fonts/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/DejaVuSans.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "DejaVuSans-Bold": [
        "/Library/Fonts/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "DejaVuSans-Oblique": [
        "/Library/Fonts/DejaVuSans-Oblique.ttf",
        "/System/Library/Fonts/Supplemental/DejaVuSans-Oblique.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
    ],
    "DejaVuSans-BoldOblique": [
        "/Library/Fonts/DejaVuSans-BoldOblique.ttf",
        "/System/Library/Fonts/Supplemental/DejaVuSans-BoldOblique.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
    ],
}


def _register_fonts() -> tuple[str, str]:
    """Retourne (FONT_NORMAL, FONT_BOLD). Fallback sur Helvetica si DejaVu absent."""
    use_dejavu = True
    for font_name, candidates in _FONT_CANDIDATES.items():
        found = next((p for p in candidates if os.path.exists(p)), None)
        if found and font_name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(font_name, found))
        elif not found:
            use_dejavu = False
            break

    if use_dejavu:
        from reportlab.lib.fonts import addMapping
        addMapping("DejaVuSans", 0, 0, "DejaVuSans")
        addMapping("DejaVuSans", 0, 1, "DejaVuSans-Oblique")
        addMapping("DejaVuSans", 1, 0, "DejaVuSans-Bold")
        addMapping("DejaVuSans", 1, 1, "DejaVuSans-BoldOblique")
        return "DejaVuSans", "DejaVuSans-Bold"

    # ReportLab built-in — toujours disponible, aucune installation nécessaire
    return "Helvetica", "Helvetica-Bold"


# ── Helpers PDF ───────────────────────────────────────────────────────────────
def make_hr(doc_width, thickness=0.6, color=colors.HexColor("#777777")):
    class HR(Flowable):
        def __init__(self):
            Flowable.__init__(self)
            self.width = doc_width
            self.height = 6

        def draw(self):
            self.canv.setStrokeColor(color)
            self.canv.setLineWidth(thickness)
            self.canv.line(0, 3, self.width, 3)

    return HR()


def role_block(company, role, dates_loc, bullets, styles_map):
    base, small, fn = styles_map["base"], styles_map["small"], styles_map["FONT_NORMAL"]
    parts = [
        Paragraph(f"<b>{company}</b> — {role}", base),
        Paragraph(dates_loc, small),
        ListFlowable(
            [ListItem(Paragraph(b, base), leftIndent=14, value="•") for b in bullets],
            bulletType="bullet",
            leftIndent=0,
            bulletFontName=fn,
            bulletFontSize=9.2,
        ),
        Spacer(1, 2.5),
    ]
    return KeepTogether(parts)


# ── Build PDF ─────────────────────────────────────────────────────────────────
def build(out_path: str) -> None:
    FONT_NORMAL, FONT_BOLD = _register_fonts()

    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=12 * mm,
    )

    _base = getSampleStyleSheet()
    base       = ParagraphStyle("base",       parent=_base["Normal"], fontName=FONT_NORMAL, fontSize=9.2,  leading=11.2)
    small      = ParagraphStyle("small",      parent=base,            fontName=FONT_NORMAL, fontSize=8.6,  leading=10.2)
    titlestyle = ParagraphStyle("titlestyle", parent=base,            fontName=FONT_BOLD,   fontSize=16,   leading=18,   spaceAfter=2)
    subtitle   = ParagraphStyle("subtitle",   parent=base,                                  fontSize=10.2, leading=12.2)
    section    = ParagraphStyle("section",    parent=base,            fontName=FONT_BOLD,   fontSize=10.4, leading=12.2, spaceBefore=6, spaceAfter=2)
    kw         = ParagraphStyle("kw",         parent=small,           textColor=colors.HexColor("#333333"))

    sm = {"base": base, "small": small, "FONT_NORMAL": FONT_NORMAL}

    def rb(company, role, dates_loc, bullets):
        return role_block(company, role, dates_loc, bullets, sm)

    story = []

    # ── En-tête ──
    story.append(Paragraph("MARTIN FELDMANN", titlestyle))
    story.append(Paragraph(
        "Data Scientist &amp; Applied Economist  •  Python pipelines, CI/CD &amp; delivery  •  Geneva",
        subtitle,
    ))
    story.append(Paragraph(
        "martin.paul.feldmann@gmail.com  |  github.com/MFE-DSS  |  linkedin.com/in/martin-paul-feldmann | +41 78 247 24 38",
        small,
    ))
    story.append(make_hr(doc.width))

    # ── About ──
    story.append(Paragraph("ABOUT", section))
    story.append(Paragraph(
        "I started in econometrics and machine learning, model diagnostics and ended up spending most of the last six years "
        "making sure data science work actually runs in production."
        "I've done this at scale (Rolex: 100+ developers, hundreds of active projects) and from scratch "
        "(Orange: built reusable components from the ground up). "
        "Right now I'm interested in analytics roles closer to markets energy, commodities, macro analysis & econometric engineering", 
        base,
    ))

    # ── Skills ──
    story.append(Paragraph("SKILLS", section))
    skills_left = [
        "<b>Econometrics / Forecasting</b> — time series, regression, ARIMA, model diagnostics, scenario framing",
        "<b>Python</b> — OOP, pandas, numpy, PySpark, SQL; reproducible pipelines from prototype to prod",
        "<b>CI/CD &amp; Delivery</b> — GitLab CI, GitHub Actions, Definition-of-Done templates",
    ]
    skills_right = [
        "<b>Infra</b> — Docker, Kubernetes, Orchestrators; containerized workloads, scheduling, smoke tests",
        "<b>Observability</b> — Monitorings, Prometheus, Grafana; log structure, alert rules, incident response basics",
    ]
    skills_table = Table(
        [[Paragraph("• " + s, base), Paragraph("• " + s2, base)] for s, s2 in zip(skills_left, skills_right)],
        colWidths=[doc.width * 0.5, doc.width * 0.5],
    )
    skills_table.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    story.append(skills_table)

    # ── Expérience ──
    story.append(Paragraph("EXPERIENCE", section))
    story.append(rb(
        "Ivy Partners SA", "AI / Data Science Lead — Consulting",
        "Apr 2024 – Present  •  Geneva",
        [
            "Own the full delivery lifecycle for analytics and ML projects: scoping, pipeline design, packaging, deployment and post-go-live monitoring.",
            "Built a Python deployment toolkit (build, smoke test, integration test, rollout)",
            "Act as technical referent for other teams: Data Science Platform Engineering",
        ],
    ))
    story.append(rb(
        "Rolex", "AI &amp; Data Science Enablement — Consultant via Ivy Partners",
        "Apr 2024 – Dec 2025  •  Geneva",
        [
            "Embedded in a large enterprise Data Science platform: 100+ developers, hundreds of projects across integration and production environments.",
            "Standardized delivery patterns for ~20 orchestrated production workloads, packaging conventions, CI/CD templates.",
            "Supported containerized deployments (Docker/K8s) and Control-M scheduling; added monitoring and alerting for scheduled jobs.",
            "Regular knowledge-sharing sessions with data scientists to close the gap between prototyping habits and production requirements.",
        ],
    ))
    story.append(rb(
        "Orange - Finance Group", "Tech Lead — Data Platform (Analytics / AI)",
        "Mar 2022 – Apr 2024  •  France",
        [
            "Led analytics programs end-to-end: translated business problems into scoped delivery with clear reliability requirements.",
            "Built internal tooling and reusable components; ran workshops to get teams aligned on shared practices.",
            "Hands-on across the stack : data ingestion, model training, API delivery, monitoring.",
        ],
    ))
    story.append(rb(
        "Orange France - Method Tools Innovation", "Python Developer — Data Pipelines",
        "Jan 2020 – Mar 2022  •  Paris",
        [
            "Built and optimized data pipelines in Python, PySpark, SQL and Hive; migrated legacy analytics workloads from SAS.",
            "Automated data quality checks and performance monitoring for scheduled production runs.",
        ],
    ))
    story.append(rb(
        "Orange", "Junior Data Scientist — Applied Econometrics / NLP (Apprenticeship)",
        "Sep 2018 – Sep 2019  •  Arcueil",
        [
            "Developed time series forecasting and KPI regression models for decision-support.",
            "Developed Econometrics applied models.",
            "Master's thesis: sentiment analysis / NLP on telecom customer data.",
        ],
    ))

    # ── Formation ──
    story.append(Paragraph("EDUCATION", section))
    for line in [
        "<b>MSc Data Science</b> — Université Paris-Est Créteil, 2018–2019",
        "<b>MSc Statistics &amp; Econometrics</b> — UPEC, 2017–2018 — thesis: regression-based forecasting of German GFCF",
        "<b>BSc Economics</b> — Université de Montpellier, 2014–2017",
        "<b>Big Data training</b> — Hadoop / Spark / HBase (2023)  •  French (native), English (C1)",
    ]:
        story.append(Paragraph(line, base))

    story.append(Spacer(1, 3))
    story.append(Paragraph(
        "<b>Stack</b>: Econometrics · Python · OOP · ML · SQL · GitHub CI/Actions · "
        "Docker · Kubernetes · Prometheus · Grafana · Azure/AWS/GCP · JIRA · Confluence",
        kw,
    ))

    doc.build(story)


# ── Entrypoint ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    args = _parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    out = os.path.join(args.output_dir, args.filename)
    build(out)
    print(f"PDF généré : {out}")
    print(f"OS détecté : {platform.system()} {platform.release()}")
