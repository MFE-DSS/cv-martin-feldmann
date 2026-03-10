# cv-martin-feldmann

Générateur de CV et lettre de motivation en PDF — Martin Feldmann.
Scripts Python autonomes, dépendance unique : `reportlab`.

## GitHub Actions — PDF automatique à chaque push

À chaque push sur n'importe quelle branche, le workflow génère les deux PDFs
et les publie comme **artifact téléchargeable** depuis l'onglet **Actions** du repo.

```
Actions → dernière exécution → Artifacts → feldmann-pdfs-<sha>
```

Les artifacts sont conservés **90 jours**.

## Installation locale

```bash
git clone https://github.com/MFE-DSS/cv-martin-feldmann.git
cd cv-martin-feldmann

python3 -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

> **macOS** : si `python3` est absent → `brew install python`

## Utilisation

```bash
# CV — sortie par défaut : ~/Desktop/CV/
python3 cv-martin-feldmann.py

# Lettre de motivation
python3 lettre-motivation.py

# Dossier personnalisé (valable pour les deux scripts)
python3 cv-martin-feldmann.py --output-dir /chemin/voulu
python3 lettre-motivation.py  --output-dir /chemin/voulu

# Via variable d'environnement
CV_OUTPUT_DIR=/chemin/voulu python3 cv-martin-feldmann.py
```

## Options (identiques sur les deux scripts)

| Option | Court | Défaut | Description |
|---|---|---|---|
| `--output-dir` | `-o` | `~/Desktop/CV` ou `$CV_OUTPUT_DIR` | Dossier de destination |
| `--filename` | `-f` | *(nom du PDF)* | Nom de fichier personnalisé |

### Détection automatique du dossier de sortie

| Contexte | Dossier utilisé |
|---|---|
| `$CV_OUTPUT_DIR` défini | valeur de la variable |
| Variable `CI=true` (GitHub Actions, etc.) | `./output/` (dans le repo) |
| Usage local | `~/Desktop/CV/` |

## Structure

```
cv-martin-feldmann/
├── .github/
│   └── workflows/
│       └── build.yml              # CI : build + upload artifact
├── cv-martin-feldmann.py          # générateur CV
├── lettre-motivation.py           # générateur lettre
├── requirements.txt
└── README.md
```
