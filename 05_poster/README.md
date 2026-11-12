# Poster scientifique

Poster A0 portrait (841 × 1189 mm) présentant le cours « Scoring financier sur données
chiffrées via FHE », affiché le jour de la soutenance (rendu séance 4, 4 janvier 2027).

Auteurs : Ravin THILAGARASA et Thomas GRUNDSZTEJN.

| Fichier | Rôle |
|---|---|
| `poster_FYC_scoring_FHE_A0.pdf` | Poster à imprimer (PDF vectoriel A0, polices embarquées) |
| `poster_apercu.png` | Aperçu basse définition |
| `poster.html` | **Source éditable** (texte, mise en page, figures SVG) |
| `assets/` | Logo ESGI, QR codes (cours Moodle, page PyPI de fhe-cli), police Roboto |
| `data/mesures.json` | Mesures affichées dans l'encadré « Résultats mesurés » |
| `scripts/benchmark.py` | Refait les mesures (score en clair, Paillier 2048 bits, CKKS) avec le code de `04_demo` |
| `scripts/benchmark_v2.py` | Mesures alignées (mêmes phases pour Paillier et CKKS, 30 répétitions, échantillons bruts conservés) : écrit `data/mesures_v2.json` et `data/mesures_v2_echantillons.csv`. **Le poster affiche encore `mesures.json`** tant que la mise à jour n'est pas validée |
| `scripts/build_poster.py` | Injecte les mesures dans le poster et génère le PDF et l'aperçu |
| `exemples/` | Posters d'exemple fournis |

## Charte

- Police : Roboto (fichiers dans `assets/fonts`, licence SIL OFL), Roboto Mono pour le code.
- Couleurs ESGI : bleu nuit `#001B40`, cyan `#00EAFF`, jaune `#FFDE00`.

## Modifier et régénérer

```bash
pip install playwright pypdf tenseal pycryptodome
python -m playwright install chromium
python 05_poster/scripts/benchmark.py      # facultatif : nouvelles mesures
python 05_poster/scripts/build_poster.py   # PDF + aperçu
```

Le poster peut aussi être ouvert directement dans un navigateur (`poster.html`) pour relire le
texte. `build_poster.py` affiche la place restante sous chaque colonne : une valeur positive
signifie que le texte déborde et doit être raccourci.
