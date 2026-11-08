# Changelog

Toutes les évolutions notables du projet sont consignées ici.
Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).
Chaque entrée est datée ; aucune section « Non publié » n'est laissée dans une version publiée.

## 2026-11-08 — Passage des images Docker à Python 3.14

### Modifié
- Images Docker de la démo et de l'atelier web : `python:3.11-slim` → `python:3.14-slim`.
  Python 3.14 est la version la plus récente pour laquelle toutes les dépendances publient
  des wheels Linux : `tenseal` 0.3.18 (et `pyyaml` 6.0.3, via `uvicorn[standard]`) s'arrêtent
  à 3.14, il n'existe pas encore de wheel pour Python 3.15.
- `numpy` 2.4.6 → 2.5.4 (démo, atelier web), possible grâce à Python ≥ 3.12.
- `fhecli` garde `requires-python = ">=3.11"` : testé sous Python 3.13 et 3.15.

Tests (images reconstruites, sans aucune compilation de paquet) :
- Démo : `/`, `/api/model`, étapes AES, Paillier, CKKS et `/api/compare` en 200 ;
  score identique en clair, avec Paillier et avec CKKS (32,0).
- Atelier web : les 10 exercices passent via l'API avec les solutions, puis réinitialisation (0/10).
- `fhecli` : 3/3 exercices résolus sous Python 3.15.

## 2026-11-08 — Mise à jour des dépendances

### Modifié
- `cryptography` 43.0.1 → 50.0.2 (démo, atelier web, `fhecli`).
- `pytest` 8.3.3 → 9.2.0 (atelier web, `fhecli`).
- `fastapi` 0.115.0 → 0.162.2 et `uvicorn[standard]` 0.30.6 → 0.54.0 (démo, atelier web).
- `tenseal` 0.3.15 → 0.3.18 et `numpy` 1.26.4 → 2.4.6 (démo, atelier web).
  `numpy` 2.5 exige Python 3.12 : la 2.4.6 est la dernière compatible avec les images `python:3.11-slim`.
- `pycryptodome` 3.20.0 → 4.4.0 (démo).
- `pyproject.toml` de `fhecli` : `pytest>=9.2,<10`, `cryptography>=50.0,<51`.

Tests (venvs Python 3.13 hors du dépôt) :
- `fhecli` : `--help`, `list`, `run` ; les 3 exercices passent avec les solutions (14 tests).
- Atelier web : les 10 exercices passent avec les solutions, y compris CKKS (37 tests) ;
  API FastAPI (liste, détail, exécution, solution, progression) en 200.
- Démo : `/`, `/api/model`, étapes AES, Paillier, CKKS et `/api/compare` en 200.

## 2026-11-08 — Carte mentale de l'introduction

### Modifié
- Carte mentale de l'introduction traduite en français et renommée
  `mind_map_Introduction.png` (faute « Introdution » corrigée).

## 2026-11-08 — Auteurs du projet

### Modifié
- Auteurs uniformisés sur Ravin THILAGARASA et Thomas GRUNDSZTEJN : métadonnées de tous les
  documents Word, PowerPoint et PDF (y compris les PDF de `step-1.zip`), page de titre de
  l'état de l'art, diapositive finale de `PPT_CAS_PRATIQUE_FHE.pptx`, `PRESENTER_NAME` de
  `build_pptx.py` et champs étudiants du modèle vidéo.
- Transcriptions vidéo corrigées (noms des intervenants). La vidéo « PRESENTATION FYC »
  sera réenregistrée.

### Ajouté
- Section « Auteurs » dans le README et champ `authors` dans le `pyproject.toml` de `fhecli`.

## 2026-11-08 — Réorganisation du dépôt

### Ajouté

- `CHANGELOG.md` (ce fichier).
- README racine avec la carte du dépôt et les liens vers chaque livrable.
- Sources de l'outil `fhe-exercices-cli` (auparavant un sous-module cassé, vide sur GitHub).
- Exceptions `.github/` et `.gitlab/` dans le `.gitignore`, pour accueillir plus tard la CI
  GitHub Actions et GitLab CI (tests, build multi-OS, publication PyPI).

### Modifié

- Réorganisation du dépôt par livrable : `00_consignes_ESGI/`, `01_recherche/`,
  `02_cours/`, `03_cas_pratiques/`, `04_demo/`, `05_poster/`, `06_video/`.
- `exercises/` renommé en `03_cas_pratiques/atelier-web/`, `demo/` en `04_demo/`.
- `CONV.MD` renommé en `01_recherche/notes_recherche_sources.md`.
- `video/videos/trasncript/` renommé en `06_video/videos/transcripts/`.
- Chemins mis à jour dans les README, le script vidéo et `build_pptx.py`.
- `.gitignore` réorganisé par sections : Python, dossiers cachés (règle `.*/` conservée,
  sauf `.github/` et `.gitlab/` pour la CI),
  fichiers système, temporaires Office, secrets.

### Supprimé

- `plan_FHE_scoring.docx` (doublon de `Plan.docx`).
- `bibliographie_FHE_scoring.docx` (ancienne version, deux auteurs erronés).
- `fhe-exercices-cli.zip` (même contenu que le dossier, régénérable).
- `SUBJECT.md` (intégré au README).
- Fichiers `__pycache__` suivis par erreur.

## 2026-11-05

### Ajouté

- Dépôt initial : plan, bibliographie, glossaire, démo web, atelier d'exercices,
  outil CLI, supports vidéo, exemples de posters.
