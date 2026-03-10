#!/usr/bin/env python3
"""
Génère Martin_Feldmann_LettreMotivation.pdf dans un dossier configurable.

Usage
-----
  python3 lettre-motivation.py
  python3 lettre-motivation.py --output-dir /tmp/cv
  CV_OUTPUT_DIR=/tmp/cv python3 lettre-motivation.py

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
    Flowable, KeepTogether, Paragraph, SimpleDocTemplate, Spacer,
)


# ── CLI / Env ────────────────────────────────────────────────────────────────
def _default_output_dir() -> str:
    if os.environ.get("CV_OUTPUT_DIR"):
        return os.environ["CV_OUTPUT_DIR"]
    if os.environ.get("CI"):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    return os.path.join(os.path.expanduser("~"), "Desktop", "CV")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Génère la lettre de motivation de Martin Feldmann en PDF.")
    p.add_argument("--output-dir", "-o", default=_default_output_dir())
    p.add_argument("--filename", "-f", default="Martin_Feldmann_LettreMotivation.pdf")
    return p.parse_args()


# ── Polices ──────────────────────────────────────────────────────────────────
_FONT_CANDIDATES = {
    "DejaVuSans": [
        "/Library/Fonts/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "DejaVuSans-Bold": [
        "/Library/Fonts/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
}


def _register_fonts() -> tuple[str, str]:
    use_dejavu = True
    for font_name, candidates in _FONT_CANDIDATES.items():
        found = next((p for p in candidates if os.path.exists(p)), None)
        if found and font_name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(font_name, found))
        elif not found:
            use_dejavu = False
            break
    if use_dejavu:
        return "DejaVuSans", "DejaVuSans-Bold"
    return "Helvetica", "Helvetica-Bold"


# ── Helpers ──────────────────────────────────────────────────────────────────
def make_hr(doc_width, thickness=0.5, color=colors.HexColor("#aaaaaa")):
    class HR(Flowable):
        def __init__(self):
            Flowable.__init__(self)
            self.width = doc_width
            self.height = 5

        def draw(self):
            self.canv.setStrokeColor(color)
            self.canv.setLineWidth(thickness)
            self.canv.line(0, 3, self.width, 3)

    return HR()


# ── Build PDF ─────────────────────────────────────────────────────────────────
def build(out_path: str) -> None:
    FONT_NORMAL, FONT_BOLD = _register_fonts()

    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=22 * mm,
        rightMargin=22 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    _base = getSampleStyleSheet()
    body    = ParagraphStyle("body",    parent=_base["Normal"], fontName=FONT_NORMAL, fontSize=10.0, leading=14.5)
    header  = ParagraphStyle("header",  parent=body,            fontName=FONT_BOLD,   fontSize=13,   leading=16,   spaceAfter=2)
    subhead = ParagraphStyle("subhead", parent=body,                                  fontSize=9.0,  leading=11.5, textColor=colors.HexColor("#555555"))
    sig     = ParagraphStyle("sig",     parent=body,            fontName=FONT_BOLD,   fontSize=10.0, leading=13)

    story = []

    # ── En-tête expéditeur ──
    story.append(Paragraph("MARTIN FELDMANN", header))
    story.append(Paragraph(
        "martinfeldmann34@gmail.com  |  Geneva, Switzerland  |  linkedin.com/in/martin-paul-feldmann",
        subhead,
    ))
    story.append(make_hr(doc.width))
    story.append(Spacer(1, 6))

    # ── Destinataire générique (à personnaliser) ──
    story.append(Paragraph("À l'attention du responsable du recrutement,", body))
    story.append(Spacer(1, 10))

    # ── Corps ──
    paragraphs = [
        (
            "Je m'appelle Martin Feldmann. Je suis data scientist de formation économétricien et macro-économiste, "
            "et je travaille depuis six ans à faire en sorte que des modèles Python finissent en production "
        ),
        (
            "Mon parcours est un peu atypique : j'ai commencé par la théorie, séries temporelles, régressions, "
            "diagnostics de modèles et je me suis retrouvé à passer la majorité de mon temps "
            "sur des pipelines CI/CD, de la conteneurisation et de l'observabilité. "
            "Chez Rolex, j'étais embarqué dans une plateforme avec plus de cent développeurs et "
            "des centaines de projets actifs en tant que Lead Technique pour la mise en production."
        ),
        (
            "Ce qui m'intéresse maintenant, c'est de ramener la partie économétrique au centre. "
            "Les marchés, l'analyse macro-economique, l'énergie, commodités, et la modélisation avancée sont des environnements où "
            "J'ai envie de travailler sur des problèmes où le modèle a des conséquences directes, "
        ),
        (
            "Je suis autonome, j'apprends vite sur les domaines métier, et je sais communiquer "
            "avec des équipes techniques autant qu'avec des non-techniciens. "
            "Je n'ai pas peur de prendre en charge un sujet de A à Z — de la question de départ "
            "jusqu'au monitoring en production."
        ),
        (
            "Je serais heureux d'échanger sur votre contexte et de voir si mon profil correspond "
            "à ce que vous cherchez. Merci pour votre attention."
        ),
    ]

    for para in paragraphs:
        story.append(Paragraph(para, body))
        story.append(Spacer(1, 9))

    # ── Signature ──
    story.append(Spacer(1, 4))
    story.append(Paragraph("Martin Feldmann", sig))
    story.append(Paragraph("Geneva — martinfeldmann34@gmail.com", subhead))

    doc.build(story)


# ── Entrypoint ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    args = _parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    out = os.path.join(args.output_dir, args.filename)
    build(out)
    print(f"PDF généré : {out}")
    print(f"OS détecté : {platform.system()} {platform.release()}")
