# fhecli : atelier CLI de chiffrement classique et FHE

Un atelier d'exercices en ligne de commande, inspiré de
[rustlings](https://github.com/rust-lang/rustlings) : vous éditez les fichiers
d'exercice dans votre propre éditeur, avec votre propre environnement Python,
et un petit outil (`fhecli`) surveille vos fichiers et relance les tests à
chaque sauvegarde.

Il accompagne le cours « Scoring financier sur données chiffrées via FHE »
(FYC, ESGI) : c'est la même progression pédagogique que l'atelier web du
projet, adaptée pour tourner directement dans votre terminal.

> **Version actuelle : 3 exercices.** Seul le module A (chiffrement
> classique) est publié pour le moment. Les modules suivants (arithmétique
> modulaire, Paillier from scratch, scoring chiffré, bonus CKKS) arriveront
> dans une prochaine mise à jour.

## Installation

Python 3.11 ou plus récent est requis.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install fhecli
fhecli init            # crée le dossier ./fhe-exercices avec les exercices
cd fhe-exercices
fhecli watch
```

`fhecli init [dossier]` crée un **espace de travail** : le dossier
`exercises/` (vos fichiers), un `pytest.ini` et un fichier marqueur
`fhecli.toml`. Les commandes de `fhecli` retrouvent cet espace depuis n'importe
quel sous-dossier. `fhecli init` refuse d'écraser un espace existant.

## Utilisation

### Mode guidé (recommandé pour commencer)

```bash
fhecli watch
```

Affiche l'exercice courant, relance ses tests à chaque fois que vous
sauvegardez le fichier, et passe automatiquement au suivant une fois qu'il est
résolu (en proposant alors d'afficher la solution de référence pour comparer).
Ctrl+C pour quitter à tout moment : rien n'est perdu, vos fichiers restent sur
le disque.

### Autres commandes

```bash
fhecli list                  # vue d'ensemble des exercices et de leur statut
fhecli run ex1_cesar         # lance les tests d'un seul exercice
fhecli hint ex1_cesar        # affiche un indice ciblé
fhecli solution ex1_cesar    # affiche la solution (une fois l'exercice résolu)
fhecli reset ex1_cesar       # remet CET exercice à son énoncé de départ (avec confirmation)
fhecli reset --all           # remet TOUS les exercices à leur énoncé de départ (avec confirmation)
fhecli reset --all -y        # idem, sans confirmation
fhecli --version
```

Codes de sortie de `fhecli run` : `0` exercice résolu, `1` tests en échec
(ou erreur), `2` tests OK mais ligne `# I AM NOT DONE` encore présente.

Vous pouvez aussi lancer les tests vous-même avec `python -m pytest` depuis
l'espace de travail : le `pytest.ini` fourni collecte bien les exercices.

## Comment marche un exercice

Chaque exercice est un unique fichier `.py` dans `exercises/`, qui contient
tout :

1. Un docstring en haut du fichier avec l'énoncé complet (contexte,
   formules, ce qu'il faut implémenter, indices).
2. Une ligne `# I AM NOT DONE` juste après : tant qu'elle est présente,
   l'exercice est considéré comme « pas terminé », même si les tests passent
   déjà. **Retirez-la vous-même** une fois satisfait de votre solution :
   c'est un geste délibérément manuel, pour vous forcer à vraiment valider
   votre travail.
3. La ou les fonctions à compléter (marquées `raise NotImplementedError`).
4. Une section de tests en bas du fichier (à ne pas modifier), exécutée par
   `pytest` à chaque `fhecli run` / `fhecli watch`.

## Solutions

La solution de référence d'un exercice est **verrouillée** tant que
l'exercice n'est pas résolu : `fhecli solution` ne l'affiche qu'une fois que
les tests passent **et** que la ligne `# I AM NOT DONE` a été retirée.

Dans le paquet, les solutions ne sont pas stockées en clair : elles sont
compressées et encodées (zlib + base64). C'est une **dissuasion**, pour
éviter de tomber sur la correction par hasard en fouillant le dossier du
paquet, **pas une protection** : rien n'empêche quelqu'un de déterminé de les
décoder. Le vrai garde-fou reste pédagogique.

## Progression (dans l'ordre suivi par `fhecli watch`)

| # | Exercice | Catégorie |
|---|----------|-----------|
| 1 | ex1_cesar | A. Chiffrement classique |
| 2 | ex2_xor_malleability | A. Chiffrement classique |
| 3 | ex3_fernet_tamper | A. Chiffrement classique |

## Développement (depuis le dépôt Scoring FHE)

Le dossier `03_cas_pratiques/fhe-exercices-cli` du dépôt est lui-même un
espace de travail (il contient `fhecli.toml`, `pytest.ini` et `exercises/`) :

```bash
cd 03_cas_pratiques/fhe-exercices-cli
python -m venv .venv
.venv\Scripts\activate          # macOS / Linux : source .venv/bin/activate
pip install -e .
fhecli watch
python -m pytest tests -q       # tests de l'outil lui-même
```

Avant de commiter : `fhecli reset --all -y`, pour ne jamais versionner de
réponses dans `exercises/`.

```
fhe-exercices-cli/
├── pyproject.toml             # empaquetage (PyPI), point d'entrée `fhecli`
├── LICENSE, MANIFEST.in
├── fhecli/                    # le paquet
│   ├── cli.py                 # commandes : init, watch, list, run, hint, solution, reset
│   ├── workspace.py           # création et recherche de l'espace de travail
│   ├── watch.py               # boucle de surveillance des fichiers
│   ├── runner.py              # exécution de pytest en sous-processus isolé
│   ├── info.py, resources.py  # liste des exercices, accès aux données du paquet
│   ├── solutions.py           # encodage / décodage des solutions
│   ├── ui.py                  # couleurs, UTF-8, confirmations
│   └── data/                  # embarqué dans le paquet (lecture seule)
│       ├── info.toml          # métadonnées des exercices (titre, catégorie, indice)
│       ├── originals/         # énoncés d'origine (fhecli init / reset)
│       └── solutions/         # solutions ENCODÉES (.sol)
├── solutions_src/             # solutions en clair : dans le dépôt, JAMAIS dans la wheel ni le sdist
├── scripts/encode_solutions.py  # régénère data/solutions/ depuis solutions_src/
├── tests/                     # tests automatisés de l'outil
├── exercises/                 # espace de travail de développement
├── fhecli.toml, pytest.ini    # marqueur et configuration de cet espace
└── requirements.txt
```

Après toute modification d'une solution dans `solutions_src/` :

```bash
python scripts/encode_solutions.py
```

Construire le paquet (sans le publier) :

```bash
python -m pip install build
python -m build                # dist/fhecli-<version>-py3-none-any.whl et .tar.gz
```

## Licence

MIT, voir [LICENSE](LICENSE).
