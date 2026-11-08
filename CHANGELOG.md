# Changelog

Toutes les évolutions notables du projet sont consignées ici.
Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).
Chaque entrée est datée ; aucune section « Non publié » n'est laissée dans une version publiée.

## 2026-11-08 — fhecli 1.2.0 : exécutables autonomes et CI

### Ajouté

- Exécutables autonomes PyInstaller, un fichier par OS (`fhecli-<version>-<os>-<arch>[.exe]`) :
  ils embarquent Python 3.15, `fhecli`, `pytest`, `cryptography` et les exercices ; aucune
  installation de Python n'est nécessaire. Code embarqué compressé (bytecode, jamais de source)
  et solutions encodées : rien n'est lisible en clair dans le binaire.
- `packaging/fhecli.spec`, `scripts/build_binary.py` (construction) et `scripts/check_binary.py`
  (parcours étudiant complet avec un PATH sans Python + recherche de texte lisible).
- CI GitHub Actions (`.github/workflows/fhecli.yml`) : tests Linux, Windows et macOS (Python 3.11
  et 3.15), exécutables Windows, Linux, macOS arm64 et x86_64, wheel et sdist ; sur un tag
  `fhecli-vX.Y.Z`, release GitHub et publication PyPI (trusted publishing).
- CI GitLab (`.gitlab-ci.yml`) : tests, exécutable Linux (Debian bookworm), wheel et sdist ;
  publication PyPI manuelle sur tag.
- Sous-commande interne `fhecli _run-pytest` : l'exécutable lance le pytest embarqué.

### Modifié

- Classifiers : ajout de Python 3.15.
- CI : action tierce `pypa/gh-action-pypi-publish` épinglée sur un commit (v1.14.3), car elle reçoit
  le droit `id-token: write` de publication sur PyPI.

Tests :

- Suite automatisée : 44/44.
- Exécutable Windows (21,8 Mo) et Linux (22,7 Mo) : 50/50 vérifications chacun ; `watch` testé
  jusqu'au bout avec le binaire Windows ; binaire Linux lancé dans un conteneur Debian sans Python.
- `.gitlab-ci.yml` validé par l'API GitLab, workflow GitHub validé par actionlint 1.7.12.

## 2026-11-08 — fhecli 1.1.0 : publiable sur PyPI

### Ajouté

- `fhecli init [dossier]` (défaut : `./fhe-exercices`) : crée un espace de travail (`exercises/`,
  `pytest.ini`, marqueur `fhecli.toml`) et refuse d'écraser un espace existant. Les autres
  commandes retrouvent l'espace en remontant depuis le dossier courant.
- `fhecli --version`, option `-y/--yes` pour `reset`.
- Fichier `LICENSE` (MIT, Ravin THILAGARASA et Thomas GRUNDSZTEJN) et `MANIFEST.in`.
- Suite de tests automatisée de l'outil (`tests/test_cli.py`, 42 tests).
- `scripts/encode_solutions.py` : régénère les solutions encodées.

### Modifié

- Énoncés, `info.toml` et solutions embarqués dans le paquet (`fhecli/data/`) : la wheel
  installée depuis PyPI fonctionne hors du dépôt, sans rien écrire dans `site-packages`.
- Solutions verrouillées : `fhecli solution` ne les affiche qu'une fois l'exercice résolu
  (tests OK et `# I AM NOT DONE` retiré) ; `watch` propose de la montrer après la réussite.
  Dans le paquet, elles sont encodées (zlib + base64, simple dissuasion) ; les sources en clair
  sont dans `solutions_src/`, exclu de la wheel et du sdist.
- `fhecli reset` et `reset --all` demandent confirmation ; Entrée, EOF et Ctrl+C valent « non »
  (plus de trace `EOFError`, y compris dans `watch`).
- `fhecli run` renvoie le code 2 quand les tests passent mais que le marqueur est présent.
- Textes de l'outil, énoncés et indices en français accentué ; sortie forcée en UTF-8
  (consoles Windows anciennes, sortie redirigée).
- `pyproject.toml` complet : README, licence, classifiers (Python 3.11 à 3.14), mots-clés,
  URLs GitHub et GitLab ; version 1.1.0 lue depuis `fhecli.__version__`.
- `watch` n'attend plus une nouvelle sauvegarde quand l'exercice est déjà résolu au moment où
  il devient l'exercice courant.

Tests :

- Suite automatisée : 42/42 sous Python 3.13 et 3.15 (Windows).
- Wheel installée hors du dépôt, sous Python 3.11 et 3.14 (Linux, Docker) : `init`, résolution
  des 3 exercices, codes de sortie, solution verrouillée puis débloquée, `reset` avec et sans
  confirmation, `pytest` à la main, `watch` jusqu'à la fin ; `site-packages` inchangé.
- Windows (Python 3.13, wheel) : PowerShell et cmd, y compris page de codes 850.
- Wheel et sdist : aucune solution en clair.

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
