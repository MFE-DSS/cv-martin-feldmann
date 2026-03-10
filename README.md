# cv-martin-feldmann

Générateur de CV PDF — Martin Feldmann.
Script Python autonome, aucune dépendance autre que `reportlab`.

## Installation rapide

```bash
git clone https://github.com/MFE-DSS/cv-martin-feldmann.git
cd cv-martin-feldmann

python3 -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

> **macOS** : si `python3` est absent → `brew install python`
> **Windows** : télécharger depuis [python.org](https://python.org)

## Utilisation

```bash
# Sortie par défaut : ~/Desktop/CV/Martin_Feldmann_CV.pdf
python3 cv-martin-feldmann.py

# Dossier personnalisé
python3 cv-martin-feldmann.py --output-dir /chemin/voulu

# Via variable d'environnement
CV_OUTPUT_DIR=/chemin/voulu python3 cv-martin-feldmann.py

# Nom de fichier personnalisé
python3 cv-martin-feldmann.py --output-dir ~/Documents --filename MF_CV_2026.pdf
```

## Options

| Option | Court | Défaut | Description |
|---|---|---|---|
| `--output-dir` | `-o` | `~/Desktop/CV` ou `$CV_OUTPUT_DIR` | Dossier de destination |
| `--filename` | `-f` | `Martin_Feldmann_CV.pdf` | Nom du fichier PDF |

## Polices

Le script détecte automatiquement DejaVu Sans (macOS, Linux).
Si absent, il bascule sur Helvetica (built-in ReportLab) — le PDF reste lisible.

## Structure

```
cv-martin-feldmann/
├── cv-martin-feldmann.py   # script principal
├── requirements.txt
└── README.md
```
