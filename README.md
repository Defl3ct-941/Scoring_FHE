# Scoring FHE

**Scoring financier sur données chiffrées via FHE : prototype et limites**

Mémoire technique (FYC, ESGI 2026-2027). Peut-on calculer un score de crédit
directement sur des données chiffrées, sans jamais les exposer en clair, et
est-ce exploitable aujourd'hui dans un contexte bancaire ?

Livrables :

- un **cours** déposé sur le Moodle de fyc.esgi.fr ;
- des **cas pratiques** sous forme d'outil Python façon rustlings (`fhecli`, publié sur PyPI) ;
- un **poster scientifique** pour présenter le cours sur un salon ;
- une **vidéo** de présentation.

## Auteurs

- Ravin THILAGARASA
- Thomas GRUNDSZTEJN

## Organisation du dépôt

| Dossier | Contenu |
| --- | --- |
| `00_consignes_ESGI/` | Consignes officielles du FYC (présentation 4A, aide visuelle) |
| `01_recherche/` | État de l'art sur le chiffrement homomorphe, notes de recherche des sources |
| `02_cours/plan/` | Plan du cours (`PLAN.md`, `Plan.docx`) |
| `02_cours/bibliographie/` | Liens bruts (`BIBLIO.md`) et bibliographie mise en forme (`Bibliographie.docx`) |
| `02_cours/glossaire/` | Glossaire (`.md`, `.docx`) et `Glossaire.xml`, export du glossaire Moodle (fyc.esgi.fr) |
| `02_cours/rendus/` | Rendus déjà déposés (`step-1.zip` = `Plan.pdf` + `Bibliographie.pdf`) |
| `03_cas_pratiques/fhe-exercices-cli/` | Outil d'exercices en ligne de commande, façon rustlings (cible PyPI) |
| `03_cas_pratiques/atelier-web/` | Version web Docker de l'atelier (10 exercices, de César à CKKS) |
| `03_cas_pratiques/Fiche_Atelier_CLI.docx` | Fiche de présentation de l'atelier CLI |
| `04_demo/` | Application web pédagogique : AES, Paillier, CKKS |
| `05_poster/` | Poster scientifique (exemples de référence dans `exemples/`) |
| `06_video/` | Script, support PPT, vidéos et transcriptions |

## Démarrage rapide

**Atelier CLI** `fhe-cli` (Python 3.11 ou plus, ou exécutable autonome sans Python) :

```bash
pip install fhe-cli
fhe-cli init          # crée le dossier fhe-exercices avec les 10 exercices
cd fhe-exercices
fhe-cli start         # lance l'atelier guidé ; fhe-cli help pour toutes les commandes
```

Prérequis système : [03_cas_pratiques/fhe-exercices-cli/SYSTEM-REQUIREMENTS.md](03_cas_pratiques/fhe-exercices-cli/SYSTEM-REQUIREMENTS.md).

**Démo web** et **atelier web** (Docker) :

```bash
cd 04_demo && docker compose up --build                       # http://localhost:8000
cd 03_cas_pratiques/atelier-web && docker compose up --build  # http://localhost:8100
```

Le détail est dans le README de chaque dossier.

## Historique

Voir [CHANGELOG.md](CHANGELOG.md).
