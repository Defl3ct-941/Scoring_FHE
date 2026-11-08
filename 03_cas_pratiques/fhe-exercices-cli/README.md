# fhe-cli : atelier de chiffrement classique et homomorphe (FHE)

Un atelier d'exercices en ligne de commande, inspiré de
[rustlings](https://github.com/rust-lang/rustlings) : vous éditez les fichiers
d'exercice dans votre propre éditeur, et `fhe-cli` relance les tests à chaque
sauvegarde, puis vous fait passer à l'exercice suivant.

Il accompagne le cours « Scoring financier sur données chiffrées via FHE »
(FYC, ESGI) : 10 exercices, du chiffrement de César à un vrai calcul FHE avec
CKKS, en passant par Paillier reconstruit à la main et un score bancaire
calculé sur données chiffrées.

## Démarrage rapide

```bash
pip install fhe-cli
fhe-cli init          # crée le dossier fhe-exercices avec les exercices
cd fhe-exercices
fhe-cli start         # lance l'atelier guidé
```

`pip install fhe-cli` installe tout, y compris TenSEAL pour le bonus CKKS :
aucune autre installation n'est nécessaire (voir les prérequis système
ci-dessous). Pour la liste des commandes : `fhe-cli help`.

## Prérequis système

Résumé ci-dessous ; détail dans [SYSTEM-REQUIREMENTS.md](SYSTEM-REQUIREMENTS.md).

### Avec pip (`pip install fhe-cli`)

| | Requis |
|---|---|
| Python | 3.11, 3.12, 3.13 ou 3.14 pour l'atelier complet ; 3.15 : tout sauf l'ex10 |
| Windows | Windows 10 ou 11, 64 bits (x86_64) |
| Linux | x86_64 ou ARM64 (aarch64), glibc 2.28+ ou musl (Alpine) |
| macOS | macOS 14 ou plus récent sur Apple Silicon (M1 à M4) |
| Espace disque | environ 150 Mo (TenSEAL, numpy, cryptography, pytest) |
| Réseau | uniquement pendant l'installation |

Le bonus **ex10 (CKKS)** utilise [TenSEAL](https://github.com/OpenMined/TenSEAL),
installé automatiquement. TenSEAL n'existe pas encore pour Python 3.15, pour
les Mac Intel, ni pour macOS 13 et antérieur : dans ces cas, `fhe-cli`
s'installe quand même et seul l'ex10 est ignoré (utilisez Python 3.14 ou
l'exécutable autonome pour le faire).

### Sans Python : exécutable autonome

| Système | Fichier | CKKS (ex10) |
|---|---|---|
| Windows 10 / 11, 64 bits | `fhe-cli-<version>-windows-x86_64.exe` | oui |
| Linux x86_64, glibc 2.35+ (Ubuntu 22.04, Debian 12 ou plus récent) | `fhe-cli-<version>-linux-x86_64` | oui |
| macOS 14+ sur Apple Silicon | `fhe-cli-<version>-macos-arm64` | oui |
| macOS sur Mac Intel | `fhe-cli-<version>-macos-x86_64` | non (ex10 ignoré) |

Chaque exécutable (40 à 50 Mo) embarque Python, `fhe-cli`, pytest,
cryptography, TenSEAL et les exercices : **aucune installation n'est
nécessaire**. Téléchargez celui de votre système dans les releases GitHub du
projet, renommez-le en `fhe-cli` (ou `fhe-cli.exe`) et placez-le dans un
dossier du `PATH`, puis utilisez-le comme dans les exemples :

```bash
# Windows (PowerShell), sans le renommer
.\fhe-cli-1.4.0-windows-x86_64.exe init
# macOS / Linux
chmod +x fhe-cli-1.4.0-linux-x86_64
./fhe-cli-1.4.0-linux-x86_64 init
```

Sous macOS, au premier lancement, autorisez le binaire dans Réglages système >
Confidentialité et sécurité (il n'est pas signé). Le code et les solutions y
sont embarqués compressés, jamais en clair.

## Commandes

| Commande | Rôle |
|---|---|
| `fhe-cli init [dossier]` | Crée votre espace de travail avec tous les exercices (par défaut : `./fhe-exercices`) |
| `fhe-cli start` | Lance l'atelier guidé : affiche l'exercice en cours, relance ses tests à chaque sauvegarde et passe au suivant une fois résolu |
| `fhe-cli list` | Affiche tous les exercices et votre progression |
| `fhe-cli run <exercice>` | Teste un exercice et affiche le résultat |
| `fhe-cli hint <exercice>` | Affiche un indice pour un exercice |
| `fhe-cli solution <exercice>` | Affiche la solution de référence (une fois l'exercice résolu) |
| `fhe-cli reset <exercice>` | Remet un exercice à son énoncé de départ (avec confirmation) |
| `fhe-cli reset --all` | Remet tous les exercices à leur énoncé de départ (`-y` : sans confirmation) |
| `fhe-cli help [commande]` | Affiche la liste des commandes, ou le détail d'une commande |
| `fhe-cli -h`, `fhe-cli --help` | Affiche la liste des commandes |
| `fhe-cli --version` | Affiche la version |

Exemples : `fhe-cli run ex1_cesar`, `fhe-cli hint ex1_cesar`,
`fhe-cli help reset`. Lancé sans argument, `fhe-cli` affiche l'aide.

Codes de sortie de `fhe-cli run` : `0` exercice résolu, `1` tests en échec
(ou erreur), `2` tests OK mais ligne `# I AM NOT DONE` encore présente.

`fhe-cli init` crée un **espace de travail** : le dossier `exercises/` (vos
fichiers), un `pytest.ini` et un fichier marqueur `fhecli.toml`. Les commandes
retrouvent cet espace depuis n'importe quel sous-dossier ; `fhe-cli init`
refuse d'écraser un espace existant. Vous pouvez aussi lancer les tests
vous-même avec `python -m pytest` depuis l'espace de travail.

Anciens noms toujours acceptés : la commande `fhecli` et `fhe-cli watch`
(équivalent de `start`). Le module Python s'appelle `fhecli`.

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
4. Une section de tests en bas du fichier (à ne pas modifier), exécutée à
   chaque `fhe-cli run` ou pendant `fhe-cli start`.

## Solutions

La solution de référence d'un exercice est **verrouillée** tant que
l'exercice n'est pas résolu : `fhe-cli solution` ne l'affiche qu'une fois que
les tests passent **et** que la ligne `# I AM NOT DONE` a été retirée.

Dans le paquet, les solutions ne sont pas stockées en clair : elles sont
compressées et encodées (zlib + base64). C'est une **dissuasion**, pour
éviter de tomber sur la correction par hasard en fouillant le dossier du
paquet, **pas une protection** : rien n'empêche quelqu'un de déterminé de les
décoder. Le vrai garde-fou reste pédagogique.

## Progression (dans l'ordre suivi par `fhe-cli start`)

| # | Exercice | Catégorie |
|---|----------|-----------|
| 1 | ex1_cesar | A. Chiffrement classique |
| 2 | ex2_xor_malleability | A. Chiffrement classique |
| 3 | ex3_fernet_tamper | A. Chiffrement classique |
| 4 | ex4_modpow | B. Briques mathématiques |
| 5 | ex5_modinv | B. Briques mathématiques |
| 6 | ex6_paillier_keygen | C. Paillier, pas à pas |
| 7 | ex7_paillier_enc_dec | C. Paillier, pas à pas |
| 8 | ex8_paillier_homomorphic | C. Paillier, pas à pas |
| 9 | ex9_scoring_paillier | D. Scoring chiffré |
| 10 | ex10_ckks_bonus | E. Bonus : FHE réel avec CKKS |

## Développement (depuis le dépôt Scoring FHE)

Le dossier `03_cas_pratiques/fhe-exercices-cli` du dépôt est lui-même un
espace de travail (il contient `fhecli.toml`, `pytest.ini` et `exercises/`) :

```bash
cd 03_cas_pratiques/fhe-exercices-cli
python -m venv .venv
.venv\Scripts\activate          # macOS / Linux : source .venv/bin/activate
pip install -e .
fhe-cli start
python -m pytest tests -q       # tests de l'outil lui-même
```

Avant de commiter : `fhe-cli reset --all -y`, pour ne jamais versionner de
réponses dans `exercises/`.

```
fhe-exercices-cli/
├── pyproject.toml             # empaquetage (PyPI : fhe-cli), commandes fhe-cli et fhecli
├── LICENSE, MANIFEST.in
├── fhecli/                    # le module Python
│   ├── cli.py                 # commandes : init, start, list, run, hint, solution, reset, help
│   ├── workspace.py           # création et recherche de l'espace de travail
│   ├── watch.py               # atelier guidé (surveillance des fichiers)
│   ├── runner.py              # exécution de pytest en sous-processus isolé
│   ├── info.py, resources.py  # liste des exercices, accès aux données du paquet
│   ├── solutions.py           # encodage / décodage des solutions
│   ├── ui.py                  # couleurs, UTF-8, confirmations
│   └── data/                  # embarqué dans le paquet (lecture seule)
│       ├── info.toml          # métadonnées des exercices (titre, catégorie, indice)
│       ├── originals/         # énoncés d'origine (fhe-cli init / reset)
│       └── solutions/         # solutions ENCODÉES (.sol)
├── solutions_src/             # solutions en clair : dans le dépôt, JAMAIS dans la wheel ni le sdist
├── scripts/                   # encode_solutions.py, build_binary.py, check_binary.py
├── packaging/                 # spécification PyInstaller (exécutables autonomes)
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
python -m build                # dist/fhe_cli-<version>-py3-none-any.whl et .tar.gz
```

## Exécutables, CI et publication

Construire et vérifier l'exécutable de l'OS courant (PyInstaller ne fait pas
de compilation croisée ; Python 3.14 pour embarquer TenSEAL) :

```bash
pip install -e . pyinstaller
python scripts/build_binary.py   # dist/fhe-cli-<version>-<os>-<arch>[.exe]
```

`scripts/build_binary.py` lance ensuite `scripts/check_binary.py`, qui
rejoue le parcours d'un étudiant avec le binaire seul (sans Python dans le
`PATH`) et vérifie qu'aucun source, aucune solution ni aucun énoncé n'apparaît
en clair dans le fichier.

La CI **GitHub Actions** (`.github/workflows/fhecli.yml`) fait tout cela
automatiquement : tests sur Linux, Windows et macOS (Python 3.11, 3.14 et 3.15),
exécutables Windows, Linux, macOS arm64 et macOS x86_64, wheel et sdist.

Pour publier une version : mettre à jour `fhecli.__version__` et le
CHANGELOG, puis pousser un tag `fhecli-vX.Y.Z` (il doit correspondre à la
version). GitHub crée alors une release avec les exécutables et publie sur
PyPI (projet `fhe-cli`, publication de confiance, sans jeton API). Une version
publiée sur PyPI ne peut pas être republiée : en cas de problème, publier la
version suivante.

## Licence

MIT, voir [LICENSE](LICENSE).
