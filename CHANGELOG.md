# Changelog

Toutes les évolutions notables du projet sont consignées ici.
Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).
Chaque entrée est datée ; aucune section « Non publié » n'est laissée dans une version publiée.

## 2026-11-10 — Brouillon du résumé personnel

### Ajouté

- Dossier `07_resume/` : brouillon de travail v0 du résumé personnel (source `resume_brouillon.md`,
  `Resume_personnel_BROUILLON_v0.docx` et `.pdf`), marqué comme brouillon sur chaque page. Il suit
  le plan du cours et reprend les mesures du prototype ; les passages personnels sont signalés
  « [À COMPLÉTER] » et les références à confirmer « [à vérifier] ». Le texte doit être réécrit par
  les auteurs avant le dépôt sur Compilatio (règlement FYC).
- Script `07_resume/scripts/build_resume.py` qui régénère le docx (Roboto, bleu nuit ESGI) et le
  PDF à partir de la source Markdown.

## 2026-11-10 — Poster scientifique

### Ajouté

- Poster scientifique A0 (`05_poster/`) : PDF vectoriel prêt à imprimer, source éditable
  `poster.html`, aperçu PNG. Charte ESGI (Roboto, bleu nuit, cyan, jaune), auteurs Ravin
  THILAGARASA et Thomas GRUNDSZTEJN, QR codes vers le cours Moodle et la page PyPI de fhe-cli.
- Mesures du prototype affichées sur le poster (`05_poster/data/mesures.json`) et scripts pour
  les refaire (`benchmark.py`) et régénérer le poster (`build_poster.py`).

## 2026-11-08 — Exécutable Linux allégé

### Modifié

- Sous Linux, les symboles de débogage de l'interpréteur embarqué (libpython, lib-dynload) sont
  retirés : l'exécutable passe sous la limite de 50 Mo de Moodle. Les bibliothèques des wheels
  (numpy.libs…) ne sont pas touchées : l'option `strip` de PyInstaller cassait leur chargement.
  L'asset Linux de la release 1.4.0 a été remplacé par cette version, sans changement de code.

## 2026-11-08 — fhe-cli 1.4.0 : commande fhe-cli, aide et prérequis système

### Ajouté

- Commande `fhe-cli help [commande]`, et aide en français pour `fhe-cli -h` / `--help` (liste
  des commandes et de leur rôle) ; `fhe-cli` lancé sans argument affiche l'aide ; erreurs
  d'utilisation en français avec renvoi vers l'aide.
- Prérequis système documentés : section du README (page PyPI) et `SYSTEM-REQUIREMENTS.md`.
- Commandes `fhe-cli next` (passe au premier exercice non résolu et lance ses tests) et
  `fhe-cli previous` (revient à l'exercice qui le précède et lance ses tests).

### Modifié

- La commande s'appelle `fhe-cli`, comme le paquet PyPI ; `fhecli` reste un alias. Toutes les
  commandes proposées et affichées (aide, messages, énoncés, documentation) utilisent `fhe-cli`,
  même via l'alias ; l'aide mentionne seulement les alias disponibles. Le module Python reste `fhecli`.
- `fhe-cli watch` devient `fhe-cli start` (« lance l'atelier guidé ») ; `watch` reste un alias.
- Tous les messages, énoncés (« Testez avec : fhe-cli run … ») et la documentation utilisent
  `fhe-cli`. Les exécutables s'appellent `fhe-cli-<version>-<os>-<arch>`.
- TenSEAL n'est plus demandé sur macOS 11 à 13 (Apple Silicon) : ses wheels exigent macOS 14,
  pip y aurait tenté une compilation et fait échouer toute l'installation ; l'ex10 y est
  ignoré. Détection par test de chaîne sur `platform_version` (Darwin 20 à 22) plutôt qu'une
  comparaison de `platform_release`, qui fait planter pip 23-24 sous Linux. Marqueur vérifié
  avec `packaging` 21.3 à 26.3 et pip 24.0 sous Linux.

## 2026-11-08 — fhe-cli 1.3.2 : TenSEAL (CKKS) inclus par défaut

### Modifié

- `pip install fhe-cli` installe tout, y compris TenSEAL pour le bonus CKKS (ex10) : l'extra
  `[ckks]` disparaît, TenSEAL devient une dépendance de base. Marqueur d'environnement
  `python_version < '3.15'` et exclusion des Mac Intel : TenSEAL 0.3.18 n'a pas de wheel pour
  Python 3.15 ni pour macOS x86_64 ; l'installation y reste possible et l'ex10 y est ignoré.
- Exécutables autonomes construits avec Python 3.14 : ils embarquent TenSEAL et numpy, l'ex10
  y fonctionne (Windows 37,5 Mo, Linux 46,2 Mo ; « 2 passed » vérifié dans chaque binaire).
- CI : tests sous Python 3.11, 3.14 et 3.15 ; exécutables, wheel et sdist construits en 3.14.
- Énoncé et indice de l'ex10 mis à jour (plus d'installation séparée à faire).

## 2026-11-08 — fhe-cli 1.3.1 : distribution PyPI renommée en fhe-cli

### Modifié

- Le paquet se publie désormais sous le nom **`fhe-cli`** (`pip install fhe-cli`, extra
  `fhe-cli[ckks]` pour le bonus CKKS) : c'est le nom du projet réservé sur PyPI. La commande
  `fhecli`, le module d'import `fhecli`, les exécutables et le dépôt gardent le nom `fhecli`.
- Les versions 1.2.0 et 1.3.0 n'ont pas été publiées sur PyPI : le nom de distribution `fhecli`
  ne correspondait pas au projet configuré pour la publication de confiance (`fhe-cli`).

## 2026-11-08 — fhe-cli 1.3.0 : atelier complet (10 exercices, de César à CKKS)

### Ajouté

- Modules B à E de l'atelier CLI, soit 7 nouveaux exercices après le chiffrement classique :
  - **B. Briques mathématiques** : `ex4_modpow` (exponentiation modulaire rapide),
    `ex5_modinv` (PGCD étendu et inverse modulaire).
  - **C. Paillier, pas à pas** : `ex6_paillier_keygen`, `ex7_paillier_enc_dec`,
    `ex8_paillier_homomorphic` (addition et multiplication par scalaire sur chiffrés).
  - **D. Scoring chiffré** : `ex9_scoring_paillier` (score bancaire calculé de bout en bout
    sans jamais déchiffrer les features).
  - **E. Bonus** : `ex10_ckks_bonus` (premier vrai calcul FHE avec CKKS / TenSEAL).
- Extra optionnel `fhe-cli[ckks]` pour le bonus (TenSEAL, dépendance native non embarquée dans
  les exécutables). Sans lui, les tests de l'ex10 sont ignorés.

### Modifié

- `fhe-cli` propose désormais 10 exercices en 5 catégories (contre 3). Suite de tests de l'outil
  étendue en conséquence.
- CI : actions GitHub passées sur Node.js 24 (`checkout` v7, `setup-python` v7, `upload-artifact` v7,
  `download-artifact` v8) ; supprime l'avertissement de dépréciation de Node.js 20.
- `start` : une sauvegarde faite pendant l'exécution des tests n'était pas détectée et bloquait
  la progression ; la date du fichier est maintenant relevée avant de lancer les tests.

## 2026-11-08 — fhe-cli 1.2.0 : exécutables autonomes et CI

### Ajouté

- Exécutables autonomes PyInstaller, un fichier par OS (`fhe-cli-<version>-<os>-<arch>[.exe]`) :
  ils embarquent Python 3.15, `fhe-cli`, `pytest`, `cryptography` et les exercices ; aucune
  installation de Python n'est nécessaire. Code embarqué compressé (bytecode, jamais de source)
  et solutions encodées : rien n'est lisible en clair dans le binaire.
- `packaging/fhecli.spec`, `scripts/build_binary.py` (construction) et `scripts/check_binary.py`
  (parcours étudiant complet avec un PATH sans Python + recherche de texte lisible).
- CI GitHub Actions (`.github/workflows/fhecli.yml`) : tests Linux, Windows et macOS (Python 3.11
  et 3.15), exécutables Windows, Linux, macOS arm64 et x86_64, wheel et sdist ; sur un tag
  `fhecli-vX.Y.Z`, release GitHub et publication PyPI (trusted publishing).
- Sous-commande interne `fhe-cli _run-pytest` : l'exécutable lance le pytest embarqué.

### Modifié

- Classifiers : ajout de Python 3.15.
- CI GitLab retirée : toute la CI et la publication PyPI passent par GitHub Actions
  (trusted publishing, sans jeton API). Le dépôt reste poussé sur GitHub et GitLab.
- CI : action tierce `pypa/gh-action-pypi-publish` épinglée sur un commit (v1.14.3), car elle reçoit
  le droit `id-token: write` de publication sur PyPI.

Tests :

- Suite automatisée : 44/44.
- Exécutable Windows (21,8 Mo) et Linux (22,7 Mo) : 50/50 vérifications chacun ; `start` testé
  jusqu'au bout avec le binaire Windows ; binaire Linux lancé dans un conteneur Debian sans Python.
- Workflow GitHub validé par actionlint 1.7.12.

## 2026-11-08 — fhe-cli 1.1.0 : publiable sur PyPI

### Ajouté

- `fhe-cli init [dossier]` (défaut : `./fhe-exercices`) : crée un espace de travail (`exercises/`,
  `pytest.ini`, marqueur `fhecli.toml`) et refuse d'écraser un espace existant. Les autres
  commandes retrouvent l'espace en remontant depuis le dossier courant.
- `fhe-cli --version`, option `-y/--yes` pour `reset`.
- Fichier `LICENSE` (MIT, Ravin THILAGARASA et Thomas GRUNDSZTEJN) et `MANIFEST.in`.
- Suite de tests automatisée de l'outil (`tests/test_cli.py`, 42 tests).
- `scripts/encode_solutions.py` : régénère les solutions encodées.

### Modifié

- Énoncés, `info.toml` et solutions embarqués dans le paquet (`fhecli/data/`) : la wheel
  installée depuis PyPI fonctionne hors du dépôt, sans rien écrire dans `site-packages`.
- Solutions verrouillées : `fhe-cli solution` ne les affiche qu'une fois l'exercice résolu
  (tests OK et `# I AM NOT DONE` retiré) ; `start` propose de la montrer après la réussite.
  Dans le paquet, elles sont encodées (zlib + base64, simple dissuasion) ; les sources en clair
  sont dans `solutions_src/`, exclu de la wheel et du sdist.
- `fhe-cli reset` et `reset --all` demandent confirmation ; Entrée, EOF et Ctrl+C valent « non »
  (plus de trace `EOFError`, y compris dans `start`).
- `fhe-cli run` renvoie le code 2 quand les tests passent mais que le marqueur est présent.
- Textes de l'outil, énoncés et indices en français accentué ; sortie forcée en UTF-8
  (consoles Windows anciennes, sortie redirigée).
- `pyproject.toml` complet : README, licence, classifiers (Python 3.11 à 3.14), mots-clés,
  URLs GitHub et GitLab ; version 1.1.0 lue depuis `fhecli.__version__`.
- `start` n'attend plus une nouvelle sauvegarde quand l'exercice est déjà résolu au moment où
  il devient l'exercice courant.

Tests :

- Suite automatisée : 42/42 sous Python 3.13 et 3.15 (Windows).
- Wheel installée hors du dépôt, sous Python 3.11 et 3.14 (Linux, Docker) : `init`, résolution
  des 3 exercices, codes de sortie, solution verrouillée puis débloquée, `reset` avec et sans
  confirmation, `pytest` à la main, `start` jusqu'à la fin ; `site-packages` inchangé.
- Windows (Python 3.13, wheel) : PowerShell et cmd, y compris page de codes 850.
- Wheel et sdist : aucune solution en clair.

## 2026-11-08 — Passage des images Docker à Python 3.14

### Modifié

- Images Docker de la démo et de l'atelier web : `python:3.11-slim` → `python:3.14-slim`.
  Python 3.14 est la version la plus récente pour laquelle toutes les dépendances publient
  des wheels Linux : `tenseal` 0.3.18 (et `pyyaml` 6.0.3, via `uvicorn[standard]`) s'arrêtent
  à 3.14, il n'existe pas encore de wheel pour Python 3.15.
- `numpy` 2.4.6 → 2.5.4 (démo, atelier web), possible grâce à Python ≥ 3.12.
- `fhe-cli` garde `requires-python = ">=3.11"` : testé sous Python 3.13 et 3.15.

Tests (images reconstruites, sans aucune compilation de paquet) :

- Démo : `/`, `/api/model`, étapes AES, Paillier, CKKS et `/api/compare` en 200 ;
  score identique en clair, avec Paillier et avec CKKS (32,0).
- Atelier web : les 10 exercices passent via l'API avec les solutions, puis réinitialisation (0/10).
- `fhe-cli` : 3/3 exercices résolus sous Python 3.15.

## 2026-11-08 — Mise à jour des dépendances

### Modifié

- `cryptography` 43.0.1 → 50.0.2 (démo, atelier web, `fhe-cli`).
- `pytest` 8.3.3 → 9.2.0 (atelier web, `fhe-cli`).
- `fastapi` 0.115.0 → 0.162.2 et `uvicorn[standard]` 0.30.6 → 0.54.0 (démo, atelier web).
- `tenseal` 0.3.15 → 0.3.18 et `numpy` 1.26.4 → 2.4.6 (démo, atelier web).
  `numpy` 2.5 exige Python 3.12 : la 2.4.6 est la dernière compatible avec les images `python:3.11-slim`.
- `pycryptodome` 3.20.0 → 4.4.0 (démo).
- `pyproject.toml` de `fhe-cli` : `pytest>=9.2,<10`, `cryptography>=50.0,<51`.

Tests (venvs Python 3.13 hors du dépôt) :

- `fhe-cli` : `--help`, `list`, `run` ; les 3 exercices passent avec les solutions (14 tests).
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

- Section « Auteurs » dans le README et champ `authors` dans le `pyproject.toml` de `fhe-cli`.

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
