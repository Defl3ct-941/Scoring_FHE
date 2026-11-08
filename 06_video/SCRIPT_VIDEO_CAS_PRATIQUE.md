# Script vidéo : Cas pratique : Scoring financier sur données chiffrées via FHE

Vidéo solo, durée cible 8 à 10 minutes. Présentation du cas pratique construit
pour le projet : le support de diapositives (`PPT_CAS_PRATIQUE_FHE.pptx`),
l'application web pédagogique (`04_demo/`) et l'atelier d'exercices pratiques
(`03_cas_pratiques/atelier-web/`).

Le PPT sert uniquement de support pour les moments où vous n'êtes **pas** sur
une page web (accroche, rappels théoriques, transitions, limites,
conclusion). Toute la partie démonstration se fait directement dans le
navigateur, sans diapositive.

---

## 🎬 Avant de filmer : checklist de préparation

- **Logiciel d'enregistrement** : OBS Studio (gratuit) ou Windows Game Bar
  (`Win+G`). Résolution 1920×1080, capture d'écran + micro.
- **Ouvrir le support de présentation** `video/PPT_CAS_PRATIQUE_FHE.pptx` en
  mode diaporama (F5), sur le même écran que vous basculerez avec le
  navigateur (Alt+Tab entre les deux, ou deux fenêtres côte à côte si vous
  enregistrez sur deux moniteurs). C'est un fichier généré à partir du thème
  `BASE_template_video_scoring_fhe.pptx` (jamais modifié) via le script
  `video/build_pptx.py` : si vous voulez changer votre nom, la date, ou un
  texte, éditez `build_pptx.py` puis relancez `python build_pptx.py`.
- **Lancer les deux applis à l'avance** (pour ne pas montrer de temps de
  build à l'écran) :
  ```bash
  cd 04_demo && docker compose up -d
  cd ../03_cas_pratiques/atelier-web && docker compose up -d
  ```
- **Réinitialiser la démo des exercices** pour repartir propre :
  `rm 03_cas_pratiques/atelier-web/data/progress.json` puis `docker compose restart` (sinon ça
  montre une progression déjà faite).
- **Onglets navigateur prêts** : `localhost:8000` (démo pédagogique) et
  `localhost:8100` (exercices). Zoom navigateur à 100-110 % pour que le texte
  soit lisible en vidéo.
- **Fermer** les notifications, autres onglets, Slack/Discord.
- **Terminal prêt** avec police lisible (16-18pt), dans le dossier
  `03_cas_pratiques/atelier-web/workspace/ex1_cesar/` par exemple pour montrer le code source si
  besoin.
- Faites **un essai audio** de 10 secondes avant de commencer pour vérifier
  le niveau du micro.
- Astuce : filmez en **plusieurs prises courtes** (intro / démo web /
  exercices / conclusion) et montez-les bout à bout, bien plus facile que de
  viser une prise unique sans erreur de 9 minutes.

---

## Découpage minuté (cible : 9 min, marge 8-10 min)

| # | Séquence | Durée | Support |
|---|----------|-------|---------|
| 1 | Accroche & problématique | 0:45 | PPT diapo 1 puis diapo 2 (« 01 : La problématique ») |
| 2 | Rappel express : c'est quoi le FHE | 1:00 | PPT diapo 3 (« Trois niveaux de chiffrement ») |
| 3 | Le scénario du projet (scoring) | 0:45 | PPT diapo 4 (schéma du pipeline) |
| · | *Transition vers la démo* | · | PPT diapo 5 (« 02 : Démonstration en direct ») |
| 4 | **Démo live : l'appli pédagogique** | 3:15 | Navigateur `localhost:8000` |
| 5 | **Démo live : les exercices** | 2:00 | Navigateur `localhost:8100` |
| · | *Transition retour slides* | · | PPT diapo 6 (« 03 : Limites & regard critique ») |
| 6 | Limites & regard critique | 1:00 | PPT diapos 7 et 8 (limites + chiffres mesurés) |
| 7 | Conclusion & perspectives | 0:45 | PPT diapo 9 puis diapo 10 (clôture) |

---

## 🗣️ SCRIPT COMPLET

### 1. Accroche & problématique : 0:00-0:45

*[PPT diapo 1 : couverture « Scoring financier sur données chiffrées via
FHE »]*

> « Bonjour, aujourd'hui je vous présente le cas pratique de mon projet :
> *Scoring financier sur données chiffrées via FHE, prototype et limites*.
>
> Le problème de départ est simple : pour calculer un score de crédit, une
> banque a besoin d'accéder aux données sensibles du client (revenus,
> endettement, incidents de paiement). Ces données doivent être en clair pour
> être traitées, ce qui pose un vrai problème de confidentialité et de
> conformité RGPD.
>
> La question à laquelle je réponds : peut-on calculer ce score **sans
> jamais voir les données en clair**, grâce au chiffrement homomorphe
> complet, le FHE ? Pour répondre à ça, j'ai construit deux outils : une
> application web pédagogique qui montre le FHE pas à pas, et une série
> d'exercices pratiques. Je vais vous montrer les deux. »

*[Avancer sur PPT diapo 2 : « 01 : La problématique »]*

---

### 2. Rappel express : c'est quoi le FHE : 0:45-1:45

*[PPT diapo 3 : « Trois niveaux de chiffrement », faites défiler les trois
icônes (bouclier, clé, puce) au fil de votre discours]*

> « Petit rappel avant la démo. Il y a trois niveaux de chiffrement à
> connaître.
>
> D'abord, le chiffrement **classique**, AES par exemple : il protège la
> donnée au repos et en transit, mais on ne peut faire aucun calcul dessus
> sans la déchiffrer.
>
> Ensuite, le chiffrement homomorphe **partiel**, comme Paillier, qui date
> de 1999 : il permet de faire des **additions** directement sur les données
> chiffrées, et des multiplications par un nombre public. C'est limité, mais
> ça suffit pour un calcul comme une somme pondérée.
>
> Enfin, le **FHE complet**, les schémas modernes comme CKKS ou TFHE :
> il permet addition ET multiplication entre deux chiffrés, sur des nombres
> réels. C'est la brique qui ouvre la porte à des modèles plus riches, mais
> elle a un coût : les données chiffrées explosent en taille, et le calcul
> devient beaucoup plus lent.
>
> C'est exactement cette progression, classique puis partiel puis complet,
> que mon application pédagogique fait vivre. »

---

### 3. Le scénario du projet : 1:45-2:30

*[PPT diapo 4 : « Le scénario : un score de crédit sans jamais montrer les
données », le schéma à droite illustre le pipeline client/serveur]*

> « Le scénario que j'utilise partout est celui du plan : un score de crédit
> calculé comme une simple somme pondérée à partir de trois données : le
> revenu, le taux d'endettement, et le nombre d'incidents de paiement. Les
> poids de cette formule sont **publics**, connus du serveur ; seules les
> données du client doivent rester secrètes. C'est cette asymétrie qui rend
> tout le reste possible.
>
> Le principe est toujours le même : le client chiffre ses données, le
> serveur calcule sans jamais les déchiffrer, et le client déchiffre le
> résultat final. C'est ce qu'on va voir tourner concrètement. »

*[Avancer sur PPT diapo 5 : « 02 : Démonstration en direct », puis basculer
vers le navigateur]*

---

### 4. Démo live : l'application pédagogique : 2:30-5:45

*[Navigateur, ouvrir `localhost:8000`]*

> « Voici l'application. Sur la gauche, mes trois données, je vais garder
> les valeurs par défaut, et le score en clair de référence, calculé en
> direct, qui va nous servir de vérité terrain tout au long de la démo. »

**Étape 0 : le scénario** *(cliquer sur l'onglet "0")*

> « La page d'accueil pose le scénario et le pipeline : le client chiffre,
> le serveur calcule sans déchiffrer, le client déchiffre le résultat. »

**Étape 1 : Chiffrement classique** *(cliquer, puis bouton "Chiffrer mes
données")*

> « Première étape : le chiffrement classique, Fernet, qui repose sur AES.
> Je chiffre mes trois valeurs, voilà les chiffrés. Maintenant je clique
> sur le bouton qui simule une tentative de calcul du serveur... et voilà :
> **InvalidToken**. Le chiffrement authentifié détecte la moindre altération
> et refuse de déchiffrer. Conclusion : confidentialité totale, mais
> **aucun calcul possible**. »

**Étape 2 : Paillier** *(cliquer, bouton "Chiffrer et calculer")*

> « Deuxième étape, Paillier, le chiffrement homomorphe partiel, que j'ai
> implémenté moi-même en Python, à la main, pas avec une librairie boîte
> noire. Je lance le calcul : le serveur multiplie chaque valeur chiffrée
> par son poids, puis additionne le tout, **sans jamais voir les données en
> clair**. Et voilà le résultat déchiffré : [lire le chiffre], identique au
> score en clair de référence. Le badge le confirme : résultat **exact**. »

**Étape 3 : FHE complet CKKS** *(cliquer, bouton "Chiffrer et calculer")*

> « Troisième étape, le FHE complet avec CKKS, via Microsoft SEAL. Ici je
> simule une vraie séparation client/serveur : le serveur ne reçoit qu'un
> contexte **public**, sans la clé secrète. Je lance le calcul... et
> regardez cette carte : le serveur **tente de déchiffrer et échoue
> explicitement**, preuve qu'il ne détient pas la clé. Le résultat final,
> déchiffré côté client cette fois, est très proche du score en clair, avec
> une toute petite erreur d'arrondi, c'est normal, CKKS travaille sur des
> approximations. Et regardez la taille des données : le facteur
> d'expansion est de l'ordre de plusieurs milliers, c'est une des limites
> concrètes du FHE, j'y reviendrai. »

**Étape 4 : Comparatif** *(cliquer, bouton "Lancer le comparatif")*

> « Dernière étape : le comparatif direct des trois approches, temps de
> calcul, taille des données chiffrées, précision. On voit clairement le
> compromis : plus on monte en puissance de calcul homomorphe, plus c'est
> lourd et lent. Et en dessous, je liste les limites réelles du FHE
> aujourd'hui : pas de comparaisons faciles sur du chiffré, bootstrapping
> coûteux, paramétrage complexe. »

---

### 5. Démo live : les exercices pratiques : 5:45-7:45

*[Navigateur, ouvrir `localhost:8100`]*

> « Pour aller plus loin que la simple démonstration, j'ai aussi construit
> un atelier de 10 exercices Python, corrigés automatiquement, qui reprennent
> exactement cette progression. »

*[Montrer la sidebar avec les modules A à E]*

> « Ils sont organisés en 5 modules : chiffrement classique, arithmétique
> modulaire (les bases mathématiques de tout schéma de chiffrement), puis
> Paillier reconstruit de zéro étape par étape, une application de
> synthèse : le score bancaire chiffré de bout en bout, et enfin un bonus
> avec du vrai FHE, CKKS via TenSEAL.
>
> Ce qui est important : chaque exercice est **verrouillé** tant que le
> précédent n'est pas réussi, impossible de sauter les étapes. »

*[Cliquer sur un exercice simple, par exemple ex1_cesar]*

> « Voici un exercice : l'énoncé, le code à compléter avec des TODO, et un
> bouton pour lancer les tests. »

*[Cliquer sur "Lancer les tests" avec le stub non complété]*

> « Sans implémentation, ça échoue proprement : pytest tourne dans un
> sous-processus isolé, avec un timeout en cas de boucle infinie. »

*[Optionnel, si le temps le permet : coller rapidement une solution ou taper
2 lignes de code en direct, relancer, montrer le badge vert « tous les tests
passent », montrer qu'un exercice suivant se déverrouille dans la sidebar]*

> « Une fois résolu, l'exercice suivant se déverrouille automatiquement. Le
> dossier de code est monté en volume Docker : je peux éditer dans mon
> éditeur habituel ou directement dans le navigateur, les deux sont
> synchronisés en temps réel. Et si je veux tout reprendre à zéro, un bouton
> de réinitialisation remet chaque exercice, ou l'atelier complet, dans son
> état de départ. »

*[Basculer vers le PPT, diapo 6 : « 03 : Limites & regard critique »]*

---

### 6. Limites & regard critique : 7:45-8:45

*[PPT diapo 7 : « Les limites réelles du FHE aujourd'hui »]*

> « Ce que cette démo met en évidence, ce sont les vraies limites du FHE
> aujourd'hui, au-delà de la théorie. Premièrement, le **surcoût
> computationnel** : un calcul homomorphe peut être des centaines de fois
> plus lent qu'en clair. Deuxièmement, l'**expansion des données** : on l'a
> vu, un facteur de plusieurs milliers pour CKKS. Troisièmement,
> l'**absence de comparaisons simples**, c'est pour ça que mon score n'est
> volontairement pas limité entre 0 et 100 : un simple `if score > seuil`
> est déjà un défi en FHE. Et enfin, le **bootstrapping**, nécessaire dès
> qu'on veut enchaîner beaucoup d'opérations, comme dans une régression
> logistique complète, c'est le principal verrou de performance
> aujourd'hui. »

*[Avancer sur PPT diapo 8 : « Ce que la démo mesure concrètement »]*

> « Pour donner des chiffres concrets, mesurés directement dans ma démo :
> Paillier renvoie un résultat **exact**, identique au score en clair. CKKS
> multiplie la taille des données par environ treize mille neuf cents. Et le
> calcul CKKS complet, chiffrement, calcul serveur, déchiffrement, prend
> environ trois cent quatre-vingts millisecondes, contre un temps quasi nul
> en clair. »

---

### 7. Conclusion & perspectives : 8:45-9:30

*[PPT diapo 9 : « Conclusion & perspectives »]*

> « Pour conclure : le FHE fonctionne, je l'ai démontré avec un vrai
> prototype fonctionnel, pas juste sur le papier. Paillier donne un
> résultat exact, CKKS un résultat approché mais avec des calculs bien plus
> riches possibles. Mais il reste aujourd'hui coûteux et complexe à mettre
> en œuvre pour un vrai système bancaire en production. Les pistes
> d'évolution sont claires : accélération matérielle GPU ou FPGA, progrès
> sur le bootstrapping, et standardisation via le NIST ou
> HomomorphicEncryption.org. »

*[Avancer sur PPT diapo 10 : « Merci de votre attention / Des questions ? »]*

> « Merci de votre attention. »

---

## Notes de montage

- Coupez les silences/hésitations entre les sections numérotées, c'est pour
  ça qu'il vaut mieux filmer section par section.
- Si une manip web rate (mauvais clic, chargement lent), refaites juste
  cette section, pas toute la vidéo.
- Ajoutez des sous-titres si l'exercice le demande, le texte exact de
  chaque section est déjà rédigé ci-dessus, copiable tel quel.
- Le minutage total est volontairement à 9:30 avec de la marge : si vous
  parlez plus vite, ajoutez 15-20s de plus dans la démo live (par exemple en
  commentant plus le code Paillier affiché à l'écran).
- Pour les captures d'écran du PPT, mode Présentation (F5) plutôt qu'un
  simple partage de fenêtre en mode édition : les diapositives occupent tout
  l'écran, sans barre d'outils PowerPoint visible.
