# Atelier d'exercices : du chiffrement classique au FHE

10 exercices Python progressifs, corrigés automatiquement, qui reprennent
pas à pas les notions montrées dans `04_demo/` : chiffrement classique,
Paillier (chiffrement homomorphe partiel) implémenté à la main, puis un
avant-goût de FHE réel avec CKKS/TenSEAL, jusqu'à un score bancaire chiffré
de bout en bout.

## Lancer l'atelier (Docker)

L'atelier est distribué comme une **image Docker autonome** : le code de
l'application, les 10 exercices, les corrections de référence et les stubs
de réinitialisation sont tous intégrés dans l'image. Aucun dossier du dépôt
n'a besoin d'être présent à côté pour la faire tourner.

```bash
cd 03_cas_pratiques/atelier-web
docker compose up --build
```

Puis ouvrir **http://localhost:8100**.

Toute l'édition de code se fait désormais **dans l'interface web** (l'éditeur
intégré), et non plus en modifiant les fichiers depuis l'hôte : comme
l'image embarque son propre contenu, un éditeur externe (VS Code...) pointé
sur `atelier-web/workspace/` ne verrait pas ce que le conteneur exécute. Seule
la progression (exercices réussis, tentatives) est conservée entre deux
lancements, dans un volume Docker nommé (`exercises-data`).

### Lancer l'image sans docker-compose

L'image peut aussi être démarrée directement, sur n'importe quelle machine
disposant de Docker, sans avoir besoin du reste du dépôt :

```bash
docker build -t fhe-exercises:latest .
docker run -p 8100:8100 fhe-exercises:latest
```

Pour conserver la progression entre deux `docker run`, ajoutez un volume :

```bash
docker run -p 8100:8100 -v fhe-exercises-data:/app/data fhe-exercises:latest
```

### Distribuer l'image (sans registre)

Pour donner l'atelier à quelqu'un qui n'a pas le dépôt, exportez l'image
construite en un seul fichier `.tar` :

```bash
docker save -o fhe-exercises.tar fhe-exercises:latest
# sur la machine de destination :
docker load -i fhe-exercises.tar
docker run -p 8100:8100 fhe-exercises:latest
```

## Progression (dans l'ordre)

| # | Exercice | Module |
|---|----------|--------|
| 1 | Chiffrement de César | A. Chiffrement classique |
| 2 | XOR et le danger de la malléabilité | A. Chiffrement classique |
| 3 | Chiffrement authentifié avec Fernet | A. Chiffrement classique |
| 4 | Exponentiation modulaire rapide | B. Arithmétique modulaire |
| 5 | PGCD étendu et inverse modulaire | B. Arithmétique modulaire |
| 6 | Générer une paire de clés Paillier | C. Paillier from scratch |
| 7 | Chiffrer et déchiffrer avec Paillier | C. Paillier from scratch |
| 8 | Propriétés homomorphes de Paillier | C. Paillier from scratch |
| 9 | Score bancaire chiffré de bout en bout | D. Application |
| 10 | (Bonus) CKKS avec TenSEAL | E. Bonus : FHE réel |

Chaque exercice est **verrouillé** tant que ses prérequis ne sont pas
réussis (visible avec un 🔒 dans l'interface), pour garder un apprentissage
dans l'ordre logique. Les exercices 1 à 3 et le bonus (10) n'ont pas de
prérequis et peuvent être faits à tout moment.

## Comment ça marche

- Chaque exercice vit dans `workspace/<id>/` : `README.md` (énoncé),
  `exercise.py` (le code à compléter, que vous éditez), `test_exercise.py`
  (les tests, en lecture seule dans l'interface, mais consultables).
- Cliquer sur **"Lancer les tests"** enregistre votre code puis exécute
  `pytest` sur `test_exercise.py` dans un sous-processus isolé (avec un
  timeout de 20s en cas de boucle infinie), et affiche le résultat.
- Un bouton **"Afficher la solution"** est disponible par prudence (avec une
  confirmation) si vous êtes vraiment bloqué, essayez d'abord sans !
- La progression est sauvegardée dans `/app/data/progress.json` **à
  l'intérieur du conteneur**, sur le volume Docker `exercises-data` (persisté
  entre deux redémarrages du conteneur, mais pas visible directement depuis
  l'hôte).

## Sans Docker (optionnel)

```bash
cd 03_cas_pratiques/atelier-web
python -m venv .venv && source .venv/bin/activate
pip install -r runner/requirements.txt
python -m pytest workspace/ex1_cesar/test_exercise.py -v   # pour un exercice donné
```

> L'exercice 10 (bonus, TenSEAL) ne fonctionne pas nativement sous Windows
> sans Docker (pas de roue précompilée). Les 9 autres n'ont besoin que de
> la bibliothèque standard et de `cryptography`.

## Structure

```
atelier-web/
├── Dockerfile                 # image autonome : app + workspace + solutions + stubs
├── docker-compose.yml
├── .dockerignore
├── data/                      # (hors image) utile seulement en usage sans Docker
├── runner/
│   ├── requirements.txt
│   └── app/
│       ├── main.py            # API FastAPI (liste, sauvegarde, exécution, reset)
│       ├── grader.py          # lance pytest en sous-processus isolé
│       ├── progress_store.py  # persistance de la progression
│       └── static/            # interface web (HTML/CSS/JS)
├── workspace/                 # les 10 exercices, intégrés dans l'image
│   └── exN_nom/
│       ├── meta.json
│       ├── README.md
│       ├── exercise.py
│       └── test_exercise.py
├── solutions/                 # corrections de référence, intégrées dans l'image
│   └── exN_nom/solution.py
└── stubs/                     # copies figées des énoncés, utilisées par le reset
    └── exN_nom/exercise.py
```

L'image construite à partir de ce dossier (`docker build -t fhe-exercises .`)
contient tout ce qui précède sauf `data/` et `docker-compose.yml` : elle se
suffit à elle-même.
