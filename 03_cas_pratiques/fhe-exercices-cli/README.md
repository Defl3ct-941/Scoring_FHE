# fhecli : atelier CLI de chiffrement classique et FHE

Un atelier d'exercices en ligne de commande, inspire de
[rustlings](https://github.com/rust-lang/rustlings) : vous ouvrez ce dossier
dans votre propre VS Code, vous editez les fichiers d'exercice avec votre
propre environnement Python, et un petit outil (`fhecli`) surveille vos
fichiers et relance les tests a chaque sauvegarde.

C'est la meme progression pedagogique que `../atelier-web/` (la version web du
projet), adaptee pour tourner directement dans votre terminal.

> **Version actuelle : 3 exercices.** Seul le module A (chiffrement
> classique) est publie pour le moment. Les modules suivants (arithmetique
> modulaire, Paillier from scratch, scoring chiffre, bonus CKKS) arriveront
> dans une prochaine mise a jour.

## Installation

Python 3.11 ou plus recent est requis (pour `tomllib`, dans la bibliotheque
standard).

```bash
cd 03_cas_pratiques/fhe-exercices-cli
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -e .
```

`pip install -e .` installe `fhecli` en mode editable : la commande
`fhecli` devient disponible dans votre venv, et pointe directement sur les
fichiers de ce dossier (vos modifications sont prises en compte
immediatement, pas besoin de reinstaller).

## Utilisation

### Mode guide (recommande pour commencer)

```bash
fhecli watch
```

Affiche l'exercice courant, relance ses tests a chaque fois que vous
sauvegardez le fichier dans votre editeur, et passe automatiquement au
suivant une fois qu'il est resolu. Ctrl+C pour quitter a tout moment (rien
n'est perdu, vos fichiers sont sur le disque comme d'habitude).

### Autres commandes

```bash
fhecli list                  # vue d'ensemble de tous les exercices et leur statut
fhecli run ex1_cesar         # lance les tests d'un seul exercice, une fois
fhecli hint ex1_cesar        # affiche un indice cible
fhecli solution ex1_cesar    # affiche la solution de reference (avec confirmation)
fhecli reset ex1_cesar       # remet CET exercice a son enonce de depart
fhecli reset --all           # remet TOUS les exercices a leur enonce de depart
```

## Comment marche un exercice

Chaque exercice est un unique fichier `.py` dans `exercises/`, qui contient
tout :

1. Un docstring en haut du fichier avec l'enonce complet (contexte,
   formules, ce qu'il faut implementer, indices).
2. Une ligne `# I AM NOT DONE` juste apres : tant qu'elle est presente,
   l'exercice est considere comme "pas termine", meme si les tests passent
   deja. **Retirez-la vous-meme** une fois satisfait de votre solution :
   c'est un geste deliberement manuel, pour vous forcer a vraiment valider
   votre travail plutot que de laisser un voyant vert defiler sans y preter
   attention.
3. Le(s) fonction(s) a completer (marquees `raise NotImplementedError`).
4. Une section de tests en bas du fichier (a ne pas modifier), executee par
   `pytest` a chaque `fhecli run` / `fhecli watch`.

Dans une prochaine mise a jour, les exercices suivants (Paillier from
scratch) reutiliseront du code ecrit dans un exercice precedent via de
simples imports entre fichiers (par exemple
`from ex5_modinv import mod_inverse`), pour reconstruire le schema brique
par brique. Les 3 exercices actuels sont chacun independants.

## Progression (dans l'ordre suivi par `fhecli watch`)

| # | Exercice | Categorie |
|---|----------|-----------|
| 1 | ex1_cesar | A. Chiffrement classique |
| 2 | ex2_xor_malleability | A. Chiffrement classique |
| 3 | ex3_fernet_tamper | A. Chiffrement classique |

## Structure

```
fhe-exercices-cli/
├── pyproject.toml           # empaquetage, point d'entree `fhecli`
├── requirements.txt         # dependances (cryptography, pytest)
├── info.toml                # metadonnees des exercices (titre, categorie, indice)
├── fhecli/                  # le code de l'outil CLI
│   ├── cli.py                # commandes : watch, list, run, hint, solution, reset
│   ├── watch.py               # boucle de surveillance des fichiers
│   ├── runner.py               # execution de pytest en sous-processus isole
│   ├── info.py                  # chargement de info.toml
│   └── ui.py                     # couleurs de terminal
├── exercises/                # les 3 exercices : c'est ICI que vous travaillez
│   └── exN_nom.py
├── solutions/                # corrections de reference (fhecli solution)
│   └── exN_nom.py
└── originals/                # copies figees des enonces (fhecli reset)
    └── exN_nom.py
```

## Sans installer le paquet

Vous pouvez aussi lancer l'outil sans `pip install -e .`, directement
depuis la racine de ce dossier :

```bash
pip install -r requirements.txt
python -m fhecli watch
```
