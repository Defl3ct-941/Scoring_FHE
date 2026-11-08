# Changelog

Toutes les évolutions notables du projet sont consignées ici.
Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).
Chaque entrée est datée ; aucune section « Non publié » n'est laissée dans une version publiée.

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
