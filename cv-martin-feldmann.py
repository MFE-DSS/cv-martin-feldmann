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
        "Data Scientist Platform Engineer  •  Python pipelines, CI/CD &amp; delivery  •  Geneva",
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
        "I started in econometrics and machine learning and ended up spending most of the last six years "
        "making sure data science work actually runs in production."
        "I've done this at scale (Rolex: 100+ developers, hundreds of active projects) and from scratch "
        "Orange Telecom end-to-end use case deployment framework."
        ,
    ))
  # ── Skills ──
  story.append(Paragraph("SKILLS", section))
  skills_left = [
      "<b>Python (Engineering &amp; Data)</b> — OOP, pandas/numpy; production-friendly scripts/services; packaging and reproducible runs",
      "<b>Data Modeling &amp; SQL</b> — relational modeling, Spark SQL queries, data reliability and validation checks",
      "<b>SDLC / Delivery</b> — Git (PRs, code reviews), Definition-of-Done checklists, release, production change validation",
  ]
  skills_right = [
      "<b>Web / APIs (practical)</b> — API validation, integration patterns for internal tools",
      "<b>Infra &amp; Operations</b> — Docker, Kubernetes, scheduling/orchestration; smoke tests; runbooks; logs/metrics/alert rules (Prometheus/Grafana)",
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
      "Ivy Partners SA", "Lead — Data Science Platform Engineering (Consulting)",
      "Apr 2024 – Present  •  Geneva",
      [
          "Led delivery for data/analytics initiatives in enterprise contexts: scoping, solution design, validation steps, and production readiness.",
          "Served as technical interface across stakeholders (data teams &amp; central IT): deployment process, environment constraints, release coordination.",
          "Built reusable delivery assets (project templates, Definition-of-Done checklists, CI gates) to standardize quality and accelerate execution across projects.",
      ],
  ))
  story.append(rb(
      "Rolex", "Data Science Platform Engineering — Consultant via Ivy Partners",
      "Apr 2024 – Dec 2025  •  Geneva",
      [
          "Embedded in a large platform context (100+ developers; hundreds of projects across integration and production environments).",
          "Industrialized delivery for ~20 orchestrated production workloads: packaging conventions, release checklists (DoD), and production validation steps.",
          "Contributed to a Python-based deployment framework: build image, smoke tests, integration tests (data validation / contract checks / non-regression), controlled rollout to production.",
          "Supported containerized deployments (Docker/K8s) and scheduling (Control-M); added logs/metrics/alert rules and dashboards (Dataiku) for scheduled jobs.",
      ],
  ))
  story.append(rb(
      "Orange - Finance Group", "Tech Lead — Data Platform (Analytics / AI)",
      "Mar 2022 – Apr 2024  •  France",
      [
          "Tech lead for data/analytics programs: translated business needs into scoped technical delivery with reliability, validation, and deployment requirements.",
          "Built reusable components and internal applications to operationalize analytics for business teams; ensured maintainability and clear ownership.",
          "Ran workshops to align teams on shared delivery standards (data quality checks, reproducibility routines, deployment practices).",
      ],
  ))
  story.append(rb(
      "Orange France - Method Tools Innovation", "Python Developer — Data &amp; Analytics Pipelines",
      "Jan 2020 – Mar 2022  •  Paris",
      [
          "Built and optimized data pipelines in Python, PySpark, SQL and Hive; participated in migration of legacy analytics workloads from SAS.",
          "Implemented data validation checks and reliability routines for scheduled production runs; performance-oriented SQL and scalable transformations.",
      ],
  ))
  story.append(rb(
      "Orange", "Junior Data Scientist — Analytics (Apprenticeship)",
      "Sep 2018 – Sep 2019  •  Arcueil",
      [
          "Built analytics models and KPIs for decision support; contributed to data preparation and validation steps around model delivery.",
          "Master's thesis: sentiment analysis / NLP on telecom customer data.",
      ],
  ))

# ── Formation ──
story.append(Paragraph("EDUCATION", section))
for line in [
    "<b>MSc Data Science</b> — Université Paris-Est Créteil, 2018–2019",
    "<b>MSc Statistics &amp; Econometrics</b> — UPEC, 2017–2018 — project: regression-based forecasting of German GFCF (2018)",
    "<b>BSc Economics</b> — Université de Montpellier, 2014–2017",
    "<b>Big Data training</b> — Hadoop / Spark / HBase (2023)  •  French (native), English (C1)",
]:
    story.append(Paragraph(line, base))

story.append(Spacer(1, 3))
story.append(Paragraph(
    "<b>Stack</b>: Python (OOP) · SQL · PySpark · Relational DBs · Git (Version Control) · "
    "GitLab CI / GitHub Actions · Docker · Kubernetes · Prometheus · Grafana · Control-M · "
    "Swagger (API validation) · JIRA · Confluence · AZUR/AWS/GCP (exposure)",
    kw,
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
