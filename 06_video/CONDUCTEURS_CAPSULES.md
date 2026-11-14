# Conducteurs des capsules vidéo (8 capsules, 70 min)

Auteurs : Ravin THILAGARASA et Thomas GRUNDSZTEJN.

Trames de tournage, pas un texte à lire. Les chiffres viennent d'un Mac M1 (TenSEAL 0.3.18,
`05_poster/data/mesures_v2.json`) : refaites les démonstrations sur votre machine avant
d'enregistrer et dites vos valeurs. Le polynôme de sigmoïde est celui de la leçon Moodle,
de la question E31 de l'examen et du poster.

| # | Capsule | Durée | Support principal |
|---|---|---|---|
| 1 | Qui voit quoi ? | 8 min | Schéma, navigateur, terminal |
| 2 | Paillier : du calcul à l'encodage | 9 min | Diapos, terminal Python |
| 3 | Comprendre les paramètres CKKS | 8 min | Diapos, terminal Python |
| 4 | Score, logit et décision | 8 min | Diapos, courbe, terminal |
| 5 | Construire une comparaison honnête | 9 min | Code, tableau de mesures |
| 6 | Corrigé du TP, parties A et B | 10 min | Terminal, navigateur |
| 7 | Corrigé du TP, partie C | 10 min | Terminal, tableur |
| 8 | Limites et choix d'architecture | 8 min | Diapos |

Préparation commune : serveur lancé (`cd 04_demo && docker compose up -d`, ou `uvicorn app.main:app`
dans `04_demo/backend`), terminal en police 16 à 18 pt, zoom navigateur 110 %, notifications coupées.
Filmer par séquences courtes.

## Capsule 1 — Qui voit quoi ? (8 min)

Objectif : à la fin, l'étudiant sait dessiner les acteurs, dire qui détient la clé secrète, et expliquer pourquoi la démo web est une simulation alors que le client séparé ne l'est pas.

À préparer : un schéma à trois acteurs (banque, prestataire de calcul, emprunteur) ; navigateur sur localhost:8000 avec les outils de développement ouverts sur l'onglet Réseau ; un terminal dans 04_demo.

| Temps | À l'écran | Idées à faire passer |
|---|---|---|
| 0:00–1:00 | Schéma des acteurs | Le scénario : une banque détient des données déjà vérifiées et délègue le calcul du score à un prestataire. Question de la capsule : qu'apprend ce prestataire ? |
| 1:00–2:30 | Schéma, on ajoute clés et flux | La banque garde la clé secrète. Le prestataire reçoit la fonction (publique), le matériel public et des chiffrés. Il voit quand même des métadonnées : tailles, horaires, nombre de requêtes. Le modèle de menace retenu : serveur honnête mais curieux (il suit le calcul, il essaie d'apprendre). |
| 2:30–4:00 | Navigateur, étape CKKS, onglet Réseau, clic sur la requête POST /api/step/ckks | Montrer le corps de la requête : {"revenu":3200,"ratio_endettement":28,"incidents":1}. Les valeurs sont parties en clair vers le serveur. Ensuite seulement, le même programme joue le client puis le serveur. La tentative de déchiffrement qui échoue montre qu'un contexte public ne déchiffre pas ; elle ne montre pas que l'hébergeur n'a rien vu. |
| 4:00–6:30 | Terminal | Lancer python client/client.py --revenu 3200 --endettement 28 --incidents 1 --trace echanges/. Lire la sortie : 18,3 pour Paillier, environ 18,29999 pour CKKS. Ouvrir echanges/paillier_requete.json : deux champs seulement, n et ciphertexts. Chercher 3200 ou 28 dedans : absent. Lister les tailles : requête Paillier de quelques Ko, chiffré CKKS d'environ 330 Ko, contexte public d'environ 34 Mo. |
| 6:30–7:30 | Schéma, deux colonnes | Comparer : démo web = un seul processus, valeurs reçues en clair, clé créée côté serveur, Paillier 512 bits. Client séparé = deux processus, clé chez le client, 2048 bits. Le serveur refuse même un contexte qui contiendrait une clé secrète. |
| 7:30–8:00 | Diapo de synthèse | Ce qui reste hors garantie et qu'on reverra en capsule 8 : rien ne prouve que le serveur a appliqué le bon modèle, ni que les entrées sont vraies. |

Pièges : ne pas dire « de bout en bout » pour la démo web ; ne pas dire que l'échec du déchiffrement « prouve la sécurité ».

Question de fin : « Dans la démo web, à quel moment précis les données cessent-elles d'être confidentielles vis-à-vis du serveur ? » (dès la requête HTTP).

## Capsule 2 — Paillier : du calcul à l'encodage (9 min)

Objectif : savoir dérouler à la main une addition et une multiplication par constante sous Paillier, expliquer l'encodage des réels et des signes, et dire ce que « exact » veut dire.

À préparer : diapo avec les trois formules ; terminal Python.

| Temps | À l'écran | Idées à faire passer |
|---|---|---|
| 0:00–2:00 | Formules | n = p·q, on calcule modulo n². Chiffrement avec g = n + 1 : c = (1 + m·n) · rⁿ mod n², r tiré au hasard. Deux propriétés : multiplier deux chiffrés additionne les messages ; élever un chiffré à la puissance k multiplie le message par k. Aucune multiplication entre deux chiffrés. La sécurité repose sur l'hypothèse de résiduosité composite décisionnelle : factoriser n casse le schéma, mais on ne sait pas montrer que les deux problèmes sont équivalents. |
| 2:00–4:00 | Terminal, petit exemple | Avec p = 11, q = 13 : n = 143, n² = 20 449. Chiffrer 20 avec r = 2 donne 11 382 ; chiffrer 7 avec r = 3 donne 11 566. Leur produit modulo n² vaut 13 999 et se déchiffre en 27. Élever le premier au cube donne 6 804, qui se déchiffre en 60. Préciser que ces tailles sont jouets, sans sécurité. Montrer que le même message chiffré deux fois donne deux chiffrés différents : c'est le rôle de r, qui doit venir d'un générateur cryptographique. |
| 4:00–5:30 | Formule du score | Le score est une somme pondérée à poids publics : exactement les deux opérations disponibles. Le serveur calcule E(x₁)^w₁ · E(x₂)^w₂ · E(x₃)^w₃ puis ajoute le biais. Paillier suffit donc à ce score ; pas besoin d'un schéma plus puissant. |
| 5:30–7:30 | Terminal ou diapo | Paillier travaille sur des entiers. Encodage au millième : revenu centré 700 → 700 000, endettement 28 → 28 000, incident 1 → 1 000 ; poids 0,005 → 5, −0,9 → −900, −10 → −10 000 ; biais à l'échelle 10⁶. Signes : un poids négatif s'obtient en inversant le chiffré modulo n² (dans l'exemple jouet, −2 × 20 se déchiffre bien en −40). Au déchiffrement, une valeur au-dessus de n/2 est lue comme négative. |
| 7:30–8:30 | Terminal | Deux limites de l'encodage. Débordement : dans l'exemple jouet, 4 × 20 = 80 dépasse n/2 = 71 et se déchiffre en −63. Avec 2048 bits et un score borné à 31 bits, la marge est énorme, mais il faut l'avoir vérifié. Arrondi : avec un endettement de 28,0001, la formule réelle donne 18,29991 et Paillier rend 18,3. L'écart de 0,00009 vient de l'arrondi, pas du chiffrement. |
| 8:30–9:00 | Synthèse | « Exact » signifie : exact sur les entiers encodés, tant qu'il n'y a pas de débordement. |

Pièges : ne pas dire que Paillier est « fondé sur la factorisation » sans nuance ; ne pas dire « exact » sans préciser sur quoi.

Question de fin : « Pourquoi le biais est-il encodé à l'échelle 10⁶ et pas 10³ ? » (il s'ajoute à des produits poids × entrée, déjà à l'échelle 10³ × 10³).

## Capsule 3 — Comprendre les paramètres CKKS (8 min)

Objectif : savoir lire poly_modulus_degree = 8192, coeff_mod_bit_sizes = [60, 40, 40, 60] et global_scale = 2^40, et dire ce que chacun autorise.

À préparer : diapo « chaîne de modules » (quatre blocs 60 / 40 / 40 / 60) ; terminal Python dans l'environnement de la démo.

| Temps | À l'écran | Idées à faire passer |
|---|---|---|
| 0:00–2:00 | Diapo slots | CKKS chiffre un vecteur de réels dans un polynôme de degré N. Avec N = 8192 on dispose de N/2 = 4096 emplacements : notre score n'en utilise que 3. Le résultat est approché : le bruit se mêle aux derniers chiffres significatifs. |
| 2:00–4:00 | Diapo échelle | Un réel x est stocké comme x · Δ arrondi, avec Δ = 2⁴⁰. Après une multiplication l'échelle devient Δ² ; un rescale retire un module de 40 bits et ramène l'échelle près de Δ, avec une petite erreur. Le premier module de 60 bits laisse environ 20 bits pour la partie entière des valeurs. Le dernier, de 60 bits aussi, sert aux changements de clé. |
| 4:00–6:00 | Terminal | Les deux modules de 40 bits du milieu sont les niveaux : deux multiplications successives au plus, sans bootstrapping. Le montrer : chiffrer 1,5, élever au carré (2,25), encore au carré (5,0625), une troisième fois : erreur scale out of bounds. Faire remarquer que le chiffré rétrécit à chaque niveau consommé : environ 332 Ko frais, 235 Ko après un niveau, 131 Ko après deux. Sécurité : c'est le couple (N, taille totale du module) qui compte. Ici 200 bits au total pour N = 8192, sous la limite d'environ 218 bits des tables du standard pour 128 bits de sécurité. |
| 6:00–7:30 | Code fhe_ckks.py puis client.py | Lien avec notre score : le produit par les poids consomme un niveau sur deux. La somme des trois emplacements se fait par rotations, qui exigent des clés de Galois : environ 33,4 Mo sur les 33,9 Mo du contexte public. Variante « terme à terme » : le serveur ne fait que les produits, le client additionne après déchiffrement ; contexte de 0,46 Mo. |
| 7:30–8:00 | Synthèse | Trois réglages, trois questions : N pour la sécurité et le nombre d'emplacements, la chaîne de modules pour la profondeur, l'échelle pour la précision. |

Pièges : ne pas dire que N = 8192 « donne 128 bits » tout seul ; ne pas dire que le rescale revient « exactement » à Δ ; ne pas appeler ce prototype « FHE complet » : il est nivelé, sans bootstrapping.

Question de fin : « Combien de multiplications successives permettrait la chaîne [60, 40, 40, 40, 60], et peut-on la garder avec N = 8192 ? » (trois ; mais elle totalise 240 bits, au-delà des 218 bits admis pour N = 8192 à 128 bits de sécurité : il faut passer à N = 16384).

## Capsule 4 — Score, logit et décision (8 min)

Objectif : distinguer un score en points, un logit, une probabilité et une décision ; savoir quand on peut éviter la sigmoïde et ce que coûte son approximation.

À préparer : courbe de la sigmoïde et du polynôme superposés sur [−8, 8] ; terminal.

| Temps | À l'écran | Idées à faire passer |
|---|---|---|
| 0:00–2:00 | Diapo vocabulaire | Notre S est un score en points, à coefficients choisis pour l'exemple : ce n'est ni une probabilité de défaut ni un modèle validé. Dans une régression logistique, z = b + Σ wᵢxᵢ est le logit, p = σ(z) la probabilité, et la décision compare p à un seuil τ. Distinguer aussi entraînement (trouver les poids) et inférence (les appliquer) : notre prototype ne fait que de l'inférence. |
| 2:00–4:00 | Courbe | La sigmoïde n'est pas un polynôme ; CKKS ne sait faire que des additions et des multiplications. On l'approche par le polynôme de la leçon : P(z) = 0,5 + 0,15012 z − 0,001593 z³. Degré 3 : deux multiplications successives, soit les deux niveaux de notre chaîne, mais seulement sur un logit fraîchement chiffré. Si z sort du produit scalaire chiffré, un niveau est déjà consommé et l'évaluation échoue (scale out of bounds) : il faudrait un module de plus, donc N = 16384. |
| 4:00–6:00 | Diapo équivalence | La sigmoïde est croissante, donc σ(z) ≥ τ équivaut à z ≥ ln(τ / (1 − τ)). Pour τ = 0,5 : z ≥ 0. Pour τ = 0,8 : z ≥ 1,386. Conséquence pratique : si le client a le droit de voir z, il déchiffre z et fait la sigmoïde ou la comparaison en clair ; aucune approximation n'est nécessaire. C'est le choix du prototype. La sigmoïde chiffrée ne devient utile que si z doit rester caché ou alimenter un calcul chiffré suivant. |
| 6:00–7:30 | Terminal, polyval | Évaluer le polynôme sous chiffrement : en z = 2 on obtient 0,787 pour une vraie valeur de 0,881. Écart maximal : 0,098 sur [−3, 3] comme sur [−4, 4], 0,114 sur [−8, 8]. En z = 8 il rend 0,885 au lieu de 0,9997. Ce polynôme reste à peu près utilisable sur tout [−8, 8], au prix d'une erreur d'environ 0,1 ; hors de cet intervalle il diverge. Il faut donc borner et normaliser les entrées. Le calcul chiffré, lui, reproduit le polynôme à 10⁻⁵ près : l'erreur vient de l'approximation, pas du chiffrement. |
| 7:30–8:00 | Synthèse | Règle de marge : si l'erreur est bornée par ε, la décision est préservée pour tous les dossiers dont le score est à plus de ε du seuil. Près du seuil, il faut mesurer le taux de désaccord. |

Pièges : ne pas présenter S comme une probabilité ; ne pas citer une erreur d'approximation sans son intervalle.

Question de fin : « Pour un seuil de probabilité de 0,5, quelle comparaison sur z remplace la sigmoïde ? » (z ≥ 0).

## Capsule 5 — Construire une comparaison honnête (9 min)

Objectif : savoir critiquer un tableau de performances et construire une mesure comparable. La capsule raconte une erreur réelle du projet et sa correction.

À préparer : benchmark.py et benchmark_v2.py côte à côte ; mesures_v2.json ; un graphique en boîtes à partir de mesures_v2_echantillons.csv.

| Temps | À l'écran | Idées à faire passer |
|---|---|---|
| 0:00–2:00 | Ancien tableau | Notre première mesure annonçait un calcul serveur de 90 ms pour Paillier contre 4,4 ms pour CKKS. Question à poser devant tout chiffre : qu'est-ce que le chronomètre entoure exactement ? |
| 2:00–5:00 | benchmark.py, fonction server() | Trouver l'erreur ensemble : la fonction commence par rechiffrer le biais avec un aléa, soit une exponentiation complète à 2048 bits, alors que le protocole ajoute ce biais public sans aléa. Mesure séparée : 131 ms avec ce rechiffrement, 4,6 ms sans. Environ 96 % du temps « serveur » n'était pas du calcul homomorphe. Autres défauts : nombres de répétitions différents selon les lignes, aucun échantillon conservé, clés générées d'un côté et pas de l'autre dans la démo, temps « réseau » qui n'était que de la sérialisation. |
| 5:00–7:00 | benchmark_v2.py et graphique | La méthode corrigée : mêmes phases pour les deux schémas (clés, chiffrement, calcul serveur, déchiffrement), 30 répétitions après échauffement, ordre alterné, échantillons bruts en CSV, médiane et quartiles. Le calcul en clair dure moins d'une microseconde : on le mesure par lots de 100 000. La machine, les versions et le commit sont écrits dans le fichier de résultats. |
| 7:00–8:30 | Nouveau tableau | Lecture : côté serveur, 4,6 ms pour Paillier, 2,4 ms pour CKKS, 0,7 ms en terme à terme : même ordre de grandeur. Dans notre implémentation, le coût de Paillier est chez le client : 379 ms pour chiffrer, 127 ms pour déchiffrer. C'est du Python sans optimisation (ni restes chinois au déchiffrement, ni précalcul de rⁿ) : une bibliothèque optimisée irait nettement plus vite. Ne pas en faire une propriété du schéma. Le coût de CKKS est le volume : 332 Ko par requête contre 1,5 Ko, plus les clés d'évaluation. Précision sur 1 000 profils à quatre décimales : l'arrondi d'encodage au millième écarte le score Paillier jusqu'à 4,5 × 10⁻⁴ de la formule réelle, CKKS jusqu'à 1,4 × 10⁻⁵. C'est un choix d'échelle, pas une limite de Paillier : encoder au millionième ferait disparaître cet écart, la clé de 2048 bits laissant toute la marge nécessaire. |
| 8:30–9:00 | Synthèse | Ce que ces chiffres ne disent pas : une seule machine, un seul processus, pas de réseau, profils synthétiques. Ils ne mesurent ni un débit en production ni la qualité d'un modèle de crédit. |

Pièges : ne pas conclure « CKKS est plus rapide que Paillier » en général ; ne pas donner un facteur multiplicatif comme une constante du FHE.

Question de fin : « Citez deux choses à vérifier avant de comparer deux temps de calcul. » (mêmes opérations dans le chronomètre, mêmes conditions de répétition).

## Capsule 6 — Corrigé du TP, parties A et B (10 min)

Ce conducteur suit l'énoncé du devoir Moodle « TP — comparer Paillier et CKKS sur un score fictif » : partie A calcul et encodage, partie B qui voit quoi, partie C mesures et conclusion, avec les profils imposés P1 (3200 ; 28 ; 1), P2 (1800 ; 45 ; 3), P3 (5200 ; 12,5 ; 0) et P4 (2750,5 ; 33,3333 ; 2).

Objectif : corriger le calcul et l'encodage (A), puis la délimitation de la confidentialité (B).

À préparer : terminal dans 04_demo, navigateur sur la démo, un tableau vide à remplir à l'écran.

| Temps | À l'écran | Idées à faire passer |
|---|---|---|
| 0:00–0:45 | Énoncé | Rappel des trois parties et de ce qui est attendu en A et B. |
| 0:45–3:00 | Tableau, profils 1 à 3 | Dérouler à la main. Profil (3200 ; 28 ; 1) : 50 + 3,5 − 25,2 − 10 = 18,3. Profil (1800 ; 45 ; 3) : 50 − 3,5 − 40,5 − 30 = −24. Profil (5200 ; 12,5 ; 0) : 50 + 13,5 − 11,25 = 52,25. Le score n'est pas borné entre 0 et 100, c'est voulu. |
| 3:00–4:45 | Tableau, colonne « encodé » | Entiers envoyés : (700 000 ; 28 000 ; 1 000), (−700 000 ; 45 000 ; 3 000), (2 700 000 ; 12 500 ; 0). Pour ces trois profils, score encodé = score réel. Quatrième profil (2750,5 ; 33,3333 ; 2) : réel 1,25253, encodé 1,2528. Erreur fréquente des copies : attribuer cet écart au chiffrement. Égalité attendue : Paillier déchiffré = référence encodée, strictement. |
| 4:45–5:30 | Terminal | Vérifier avec le client : python client/client.py --schema paillier --revenu 2750.5 --endettement 33.3333 --incidents 2. Lire les deux lignes d'écart : non nul face à la formule en clair, nul face à la référence encodée. |
| 5:30–7:30 | Navigateur, onglet Réseau | Partie B, version web. Tracer le chemin : le navigateur envoie les valeurs en clair, le serveur les reçoit, puis génère lui-même les clés. Le clair et la clé secrète sont tous deux côté serveur. Erreur fréquente : conclure à la confidentialité parce qu'une variable s'appelle « serveur » ou parce que le déchiffrement simulé échoue. |
| 7:30–9:15 | Terminal, dossier echanges/ | Version séparée : relancer le client avec --trace echanges/, ouvrir les fichiers. Ce qui sort du client : n et trois chiffrés pour Paillier ; un contexte public et un chiffré pour CKKS. Ce qui n'en sort pas : valeurs, λ, μ, clé secrète CKKS. Dessiner les deux schémas côte à côte. |
| 9:15–10:00 | Synthèse | Énoncé de menace attendu dans une bonne copie : confidentialité des entrées face à un serveur honnête mais curieux, sous les hypothèses du schéma et avec un client sain. Hors périmètre : intégrité du calcul, véracité des entrées, métadonnées. |

Erreurs typiques à citer : oublier de centrer le revenu sur 2500 ; confondre 28 % et 0,28 ; oublier l'échelle 10⁶ au décodage ; écrire « de bout en bout » pour la version web.

## Capsule 7 — Corrigé du TP, partie C (10 min)

Objectif : montrer une mesure reproductible, lire les distributions et formuler une conclusion défendable.

À préparer : terminal à la racine du dépôt ; mesures_v2_echantillons.csv ouvert dans un tableur avec un graphique prêt ; le rapport type de 2 à 4 pages en plan.

| Temps | À l'écran | Idées à faire passer |
|---|---|---|
| 0:00–1:00 | Énoncé | Ce qui est demandé : mesurer Paillier et CKKS sur plusieurs profils, isoler les phases, conserver les échantillons, comparer les erreurs, conclure. |
| 1:00–4:00 | Terminal | Lancer python 05_poster/scripts/benchmark_v2.py (compter environ une minute). Pendant l'exécution, commenter le code : échauffement, alternance des phases, 30 répétitions. Ouvrir mesures_v2.json : d'abord le bloc machine (processeur, mémoire, versions, commit), parce qu'un temps sans contexte ne vaut rien. |
| 4:00–6:00 | Tableur | Lire une distribution : médiane, quartiles, extrêmes. Montrer une valeur aberrante réelle (une exécution du calcul serveur Paillier à 49 ms pour une médiane de 4,6 ms) et expliquer pourquoi on publie la médiane et pas la moyenne. Génération de clés Paillier très dispersée (de 290 à 800 ms) : la recherche de nombres premiers est aléatoire. |
| 6:00–8:00 | Bloc erreurs | Trois lignes à distinguer : encodage contre formule réelle (jusqu'à 4,5 × 10⁻⁴), Paillier contre référence encodée (aucun écart sur 50 profils), CKKS contre formule réelle (jusqu'à 1,4 × 10⁻⁵). Effet de la réutilisation des clés : la génération se paie une fois par session, pas par score. Effet du seuil : un dossier dont le score est à moins de l'erreur du seuil peut changer de décision. |
| 8:00–9:30 | Plan du rapport | Conclusion attendue : pour ce score linéaire, les deux schémas répondent en quelques millisecondes côté serveur ; dans notre implémentation Python, Paillier coûte au client, CKKS coûte en volume ; l'erreur est très inférieure à toute marge métier plausible. Et ce qu'on ne peut pas conclure : rien sur un modèle non linéaire, sur le réseau, sur la charge ou sur la qualité du score. |
| 9:30–10:00 | Synthèse | Contenu minimal d'un rendu : rapport, CSV, description de l'environnement, commande de reproduction. |

Erreurs typiques à citer : chronométrer la génération des clés dans le calcul ; comparer des machines différentes ; arrondir les résultats avant de calculer l'erreur ; donner une moyenne sur trois essais.

## Capsule 8 — Limites et choix d'architecture (8 min)

Objectif : savoir dire ce que le chiffrement homomorphe ne garantit pas, et choisir entre les approches pour un scénario donné.

À préparer : tableau « question / ce que le FHE apporte / ce qui reste à traiter » ; tableau comparatif des alternatives.

| Temps | À l'écran | Idées à faire passer |
|---|---|---|
| 0:00–2:00 | Tableau, ligne intégrité | Le serveur peut renvoyer un chiffré valide d'un autre calcul : le client ne s'en aperçoit pas. Le chiffrement homomorphe protège la confidentialité des entrées, pas l'exactitude du calcul. Pistes : version de modèle annoncée, contrôles par recalcul sur échantillon, preuves de calcul si le scénario l'exige. De même, chiffrer un revenu faux ne le rend pas vrai. |
| 2:00–4:00 | Tableau, ligne sorties | Le chiffrement protège les données pendant le calcul, pas ce que révèle le résultat : quiconque reçoit le score déchiffré apprend une combinaison des entrées, et il faut décider qui y a droit. Point propre à CKKS (Li et Micciancio, 2021) : le résultat déchiffré contient un peu du bruit, et le publier tel quel à un adversaire peut affaiblir la sécurité. Il faut donc une politique de sortie ; cela ne veut pas dire que CKKS est cassé. |
| 4:00–6:00 | Tableau des alternatives | TLS et chiffrement au repos : indispensables, mais le calcul se fait en clair. Enclave matérielle : rapide, calcul ordinaire, confiance dans le fabricant et l'attestation, canaux auxiliaires. Calcul multipartite : pas de tiers unique de confiance, beaucoup d'échanges réseau, garanties selon le nombre de participants corrompus. Confidentialité différentielle : borne ce qu'une statistique révèle sur un individu ; ne chiffre pas une entrée. Les approches se combinent. |
| 6:00–7:30 | Diapo bilan | Réponse à la problématique, sous conditions. Oui : un score linéaire se calcule sur données chiffrées en quelques millisecondes, avec une erreur négligeable. Mais pour trois variables et une formule publique, calculer localement est plus simple : l'intérêt apparaît avec un modèle coûteux, un grand volume ou une contrainte d'organisation. Et « exploitable en banque » demande davantage : modèle validé, intégrité, gestion des clés, obligations réglementaires que le chiffrement ne remplace pas. |
| 7:30–8:00 | Clôture | Renvoi vers l'examen et le glossaire. |

Pièges : pas de « toujours » ni de « jamais » ; ne pas présenter un déploiement d'un autre domaine comme preuve pour le scoring bancaire ; ne pas dire que la confidentialité différentielle rend l'inférence « impossible ».

Question de fin : « Un prestataire renvoie un score chiffré : citez deux choses que le client ne peut pas vérifier. » (le modèle appliqué, l'intégrité du résultat).

## Annexe — commandes testées

À lancer dans l'environnement Python de 04_demo/backend.

Capsule 2, exemple jouet :

```python
p, q = 11, 13; n = p*q; n2 = n*n; lam = (p-1)*(q-1); mu = pow(lam, -1, n)
enc = lambda m, r: (1 + (m % n)*n) * pow(r, n, n2) % n2
def dec(c):
    m = ((pow(c, lam, n2) - 1)//n * mu) % n
    return m - n if m > n//2 else m
c1, c2 = enc(20, 2), enc(7, 3)          # 11382, 11566
dec(c1*c2 % n2)                          # 27
dec(pow(c1, 3, n2))                      # 60
dec(pow(pow(c1, -1, n2), 2, n2))         # -40
dec(pow(c1, 4, n2))                      # -63 : débordement, 80 > n/2```

Capsules 3 et 4, niveaux et sigmoïde :

```python
import tenseal as ts
ctx = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=8192,
                 coeff_mod_bit_sizes=[60, 40, 40, 60])
ctx.global_scale = 2**40
v = ts.ckks_vector(ctx, [1.5])
v = v*v; v.decrypt()      # ~2.25
v = v*v; v.decrypt()      # ~5.0625
v = v*v                   # ValueError: scale out of bounds
ts.ckks_vector(ctx, [2.0]).polyval([0.5, 0.15012, 0, -0.001593]).decrypt()   # ~0.787
ts.ckks_vector(ctx, [8.0]).polyval([0.5, 0.15012, 0, -0.001593]).decrypt()   # ~0.885```

Capsules 1, 6 et 7 :

```bash
python client/client.py --revenu 3200 --endettement 28 --incidents 1 --trace echanges/
python client/client.py --schema paillier --revenu 2750.5 --endettement 33.3333 --incidents 2
python client/client.py --schema ckks --mode terms
python 05_poster/scripts/benchmark_v2.py
```

## Points à valider avant d'enregistrer

- L'énoncé du TP sur Moodle suit désormais les parties A, B, C des capsules 6 et 7 (fait le 14 novembre).
- Qui enregistre quoi entre Ravin et Thomas.
- La limite de 218 bits citée en capsule 3 est celle du tableau du standard HomomorphicEncryption.org (N = 8192, 128 bits de sécurité classique, secret ternaire) : la citer avec sa source.
- La présentation d'équipe à réenregistrer n'est pas couverte ici : son texte doit venir de vous.
