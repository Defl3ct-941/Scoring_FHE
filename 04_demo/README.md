# Démo pédagogique : Scoring financier sur données chiffrées via FHE

Application web interactive qui montre, étape par étape, la différence entre :

1. **Chiffrement classique** (AES/Fernet), sûr, mais aucun calcul possible sur le chiffré.
2. **Chiffrement homomorphe partiel** (Paillier, implémenté à la main), qui permet une
   addition et une multiplication par un scalaire clair, ce qui suffit à un score linéaire pondéré.
3. **FHE complet** (CKKS, via Microsoft SEAL / TenSEAL), qui permet une addition et une multiplication
   entre deux chiffrés, sur des réels, avec une vraie séparation client/serveur
   (le serveur ne détient jamais la clé secrète).
4. **Comparatif & limites** : temps de calcul, taille des données chiffrées,
   précision, et les limites réelles du FHE aujourd'hui.

Le scénario métier est celui du projet : un score de crédit calculé à partir de
trois indicateurs (revenu, taux d'endettement, incidents de paiement), sans que
le serveur n'ait jamais accès aux valeurs en clair.

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

- Les tailles de clés Paillier (512 bits) sont réduites pour que la démo reste
  instantanée dans un navigateur ; des paramètres réels utiliseraient des clés
  bien plus grandes.
- Le score n'est volontairement pas "clampé" entre 0 et 100 : une comparaison
  (`if score > seuil`) est une opération non-linéaire difficile à faire
  directement sur des données chiffrées, ce qui illustre une limite concrète
  du FHE.
- Le calcul CKKS est **approximatif** par construction (bruit numérique) :
  l'erreur absolue affichée entre le résultat déchiffré et le score en clair
  de référence est normale et attendue.
