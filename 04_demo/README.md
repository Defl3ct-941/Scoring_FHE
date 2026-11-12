# Démo pédagogique : Scoring financier sur données chiffrées via FHE

Application web interactive qui montre, étape par étape, la différence entre :

1. **Chiffrement classique** (AES/Fernet), sûr, mais aucun calcul possible sur le chiffré.
2. **Chiffrement homomorphe partiel** (Paillier, implémenté à la main), qui permet une
   addition et une multiplication par un scalaire clair, ce qui suffit à un score linéaire pondéré.
3. **CKKS** (via Microsoft SEAL / TenSEAL), qui permet une addition et une multiplication
   entre deux chiffrés, sur des réels approchés. Il est utilisé ici en mode nivelé, sans bootstrapping.
4. **Comparatif & limites** : temps de calcul, taille des données chiffrées,
   précision, et les limites réelles du FHE aujourd'hui.

Le scénario métier est celui du projet : un score de crédit calculé à partir de
trois indicateurs (revenu, taux d'endettement, incidents de paiement), sans que
le serveur n'ait accès aux valeurs en clair.

## Deux niveaux à ne pas confondre

| | Démo web pas à pas (`/api/step/*`) | Client séparé (`/api/v2` + `client/client.py`) |
|---|---|---|
| But | Montrer les calculs étape par étape | Montrer une vraie séparation de confiance |
| Ce que reçoit le serveur | Les trois valeurs **en clair** (JSON) | Uniquement des chiffrés et du matériel public |
| Clé secrète | Créée dans le processus serveur (simulation) | Créée et gardée par le client, autre processus |
| Clé Paillier | 512 bits, aucune sécurité | 2048 bits |

Seul le second niveau permet de dire que l'hébergeur ne voit pas les données, et seulement
contre un serveur honnête mais curieux : rien ne prouve que le serveur applique le bon modèle,
ni que les entrées sont vraies.

## Client séparé

Serveur lancé (Docker ou `uvicorn`), dans un autre terminal :

```bash
cd 04_demo
pip install -r backend/requirements.txt -r backend/requirements-dev.txt
python client/client.py --revenu 3200 --endettement 28 --incidents 1 --trace echanges/
python client/client.py --schema ckks --mode terms
```

`--trace` enregistre les octets réellement échangés, pour vérifier soi-même qu'ils ne contiennent
ni valeur en clair ni clé secrète. `--mode terms` fait calculer au serveur les produits poids × entrée
sans les additionner : plus besoin de clés de rotation, le contexte public passe d'environ 34 Mo à 0,46 Mo.

## Tests

```bash
cd 04_demo/backend
python -m pytest tests -q
```

## Lancer la démo (Docker)

```bash
cd 04_demo
docker compose up --build
```

Puis ouvrir **http://localhost:8000** dans un navigateur.

Le premier build peut prendre quelques minutes (compilation de TenSEAL /
Microsoft SEAL si aucune roue précompilée ne correspond à la plateforme).

## Sans Docker (optionnel)

```bash
cd 04_demo/backend
python -m venv .venv && source .venv/bin/activate  # ou .venv\Scripts\activate sous Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

> TenSEAL ne fournit pas de roue précompilée pour Windows : sous Windows sans
> Docker, l'étape 3 (FHE/CKKS) ne fonctionnera pas nativement. Utilisez Docker
> ou WSL2/Linux/macOS pour cette partie.

## Structure

```
04_demo/
├── docker-compose.yml
└── backend/
    ├── Dockerfile
    ├── requirements.txt
    └── app/
        ├── main.py            # API FastAPI + service des fichiers statiques
        ├── config.py          # modèle de scoring (features, poids, biais)
        ├── crypto/
        │   ├── classic_aes.py # étape 1 : chiffrement classique
        │   ├── paillier.py    # étape 2 : Paillier (PHE) implémenté à la main
        │   └── fhe_ckks.py    # étape 3 : FHE complet (CKKS/TenSEAL)
        └── static/            # interface web (HTML/CSS/JS, sans dépendance externe)
```

## Notes pédagogiques

- Dans la démo web, les clés Paillier (512 bits) sont réduites pour que l'affichage reste
  instantané : elles n'offrent aucune sécurité. Le client séparé et les mesures utilisent 2048 bits.
- Paillier est exact sur les entiers encodés (entrées arrondies au millième). Si une entrée a plus
  de trois décimales, l'écart à la formule sur les réels vient de cet arrondi, pas du chiffrement.
- Le score n'est volontairement pas "clampé" entre 0 et 100 : une comparaison
  (`if score > seuil`) est une opération non-linéaire difficile à faire
  directement sur des données chiffrées, ce qui illustre une limite concrète
  du FHE.
- Le calcul CKKS est **approximatif** par construction (bruit numérique) :
  l'erreur absolue affichée entre le résultat déchiffré et le score en clair
  de référence est normale et attendue.
