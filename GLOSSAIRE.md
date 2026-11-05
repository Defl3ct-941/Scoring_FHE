# Glossaire du projet

Lexique des termes techniques liés au chiffrement classique et au
chiffrement homomorphe (FHE), classés par thème.

---

## 1. Cryptographie générale

**Chiffrement symétrique**
Chiffrement où la même clé sert à chiffrer et à déchiffrer. Rapide, mais la
clé doit être partagée entre les deux parties à l'avance.

**Chiffrement asymétrique**
Chiffrement à deux clés distinctes : une clé publique (pour chiffrer) et une
clé privée (pour déchiffrer). La clé publique peut être distribuée sans
risque particulier ; seule la clé privée permet de déchiffrer.

**Clé publique / clé privée (clé secrète)**
La clé publique peut être partagée sans compromettre la sécurité. La clé
privée ne doit jamais quitter son détenteur : elle seule permet de
déchiffrer.

**Texte clair (plaintext) / texte chiffré (ciphertext)**
Le texte clair est la donnée d'origine, lisible. Le texte chiffré est son
résultat après chiffrement, illisible sans la clé.

**Malléabilité**
Propriété (souvent indésirable) d'un chiffrement où l'on peut modifier le
texte chiffré de façon prévisible pour changer le texte clair correspondant,
sans connaître la clé. Dangereuse en sécurité classique, mais c'est aussi le
principe qui rend possible le calcul homomorphe.

**Chiffrement authentifié**
Chiffrement qui garantit à la fois la confidentialité (personne ne lit sans
la clé) et l'intégrité (toute altération du message est détectée au
déchiffrement).

**Nonce / IV (vecteur d'initialisation)**
Valeur aléatoire à usage unique injectée dans un chiffrement pour que
chiffrer deux fois le même message donne deux résultats différents.

---

## 2. Chiffrement classique

**Chiffrement de César**
Chiffrement historique par décalage circulaire de chaque lettre de
l'alphabet d'un nombre fixe de positions.

**XOR (ou exclusif)**
Opération bit à bit pouvant servir de chiffrement symétrique élémentaire
(`clair XOR clé = chiffré`, et `chiffré XOR clé = clair`). Exemple classique
utilisé pour illustrer la malléabilité.

**AES (Advanced Encryption Standard)**
Standard de chiffrement symétrique par blocs, très largement utilisé en
production.

**Fernet**
Format de chiffrement authentifié de haut niveau (AES en mode CBC + HMAC
pour l'intégrité + horodatage), fourni par certaines bibliothèques
cryptographiques Python courantes.

**HMAC**
Code d'authentification de message basé sur une fonction de hachage,
utilisé pour détecter toute altération d'un texte chiffré.

---

## 3. Arithmétique modulaire

**Modulo**
Reste de la division euclidienne d'un nombre par un autre. Base de
l'arithmétique utilisée par la plupart des schémas de chiffrement à clé
publique (RSA, Paillier...).

**Exponentiation modulaire rapide**
Calcul de `a^b mod n` sans jamais manipuler le nombre entier `a^b` (qui
serait gigantesque), par élévations au carré successives.

**PGCD étendu (algorithme d'Euclide étendu)**
Variante de l'algorithme du plus grand commun diviseur qui calcule en plus
les coefficients de Bézout, permettant d'obtenir un inverse modulaire.

**Inverse modulaire**
Le nombre `x` tel que `(a * x) mod n = 1`. Utilisé notamment dans le
déchiffrement de certains schémas à clé publique.

---

## 4. Chiffrement homomorphe : notions générales

**Chiffrement homomorphe**
Famille de chiffrements qui permettent d'effectuer des calculs (additions,
multiplications...) directement sur des données chiffrées, sans jamais les
déchiffrer, le résultat déchiffré correspondant au résultat qu'on aurait
obtenu en calculant sur les données en clair.

**PHE (Partially Homomorphic Encryption / chiffrement partiellement
homomorphe)**
Ne supporte qu'une seule opération homomorphe (par exemple uniquement
l'addition, ou uniquement la multiplication), mais un nombre illimité de
fois.

**SHE (Somewhat Homomorphic Encryption)**
Supporte addition et multiplication, mais seulement un nombre limité
d'opérations avant que le bruit accumulé ne rende le résultat inexploitable.

**FHE (Fully Homomorphic Encryption / chiffrement totalement homomorphe)**
Supporte un nombre illimité d'additions et de multiplications, grâce au
bootstrapping.

**Bruit (noise)**
Petite perturbation aléatoire ajoutée à chaque chiffrement pour garantir la
sécurité. Chaque opération homomorphe (surtout la multiplication) augmente
ce bruit ; au-delà d'un certain seuil, le déchiffrement devient incorrect.

**Bootstrapping**
Opération qui « rafraîchit » un texte chiffré bruité en réduisant son bruit
accumulé, sans le déchiffrer, ce qui permet de chaîner un nombre illimité
d'opérations. C'est ce mécanisme qui transforme un schéma SHE en véritable
FHE.

**Expansion ratio**
Rapport entre la taille d'une donnée chiffrée et la taille de la donnée en
clair d'origine. Sert à illustrer concrètement le coût du chiffrement
homomorphe en espace de stockage ou en bande passante réseau.

---

## 5. Paillier

**Cryptosystème de Paillier**
Schéma de chiffrement asymétrique publié par Pascal Paillier en 1999,
homomorphe additif : multiplier deux textes chiffrés Paillier produit le
chiffré de la somme des deux textes clairs correspondants.

**n, g, lambda (λ), mu (μ)**
Paramètres du schéma Paillier : `n` est le module public (produit de deux
grands nombres premiers), `g` un générateur, `lambda` et `mu` font partie de
la clé privée utilisée pour le déchiffrement.

**Addition homomorphe (Paillier)**
Multiplier deux textes chiffrés Paillier (modulo `n²`) produit le chiffré
de la somme des deux textes clairs.

**Multiplication par un scalaire en clair (Paillier)**
Élever un texte chiffré Paillier à la puissance d'un entier clair produit le
chiffré du produit correspondant. Permet d'appliquer des coefficients
connus (non chiffrés) à des données chiffrées.

**Représentation symétrique (nombres négatifs)**
Paillier travaille nativement sur des entiers positifs modulo `n`. Pour
représenter des nombres négatifs, on réinterprète les valeurs proches de
`n` comme des nombres négatifs (`valeur - n` si `valeur > n/2`).

**Mise à l'échelle en entiers (scaling)**
Paillier ne travaille que sur des entiers. Des nombres décimaux doivent
donc être multipliés par une constante d'échelle avant chiffrement, puis
divisés par cette même constante au déchiffrement.

---

## 6. CKKS et le FHE réel

**CKKS (Cheon-Kim-Kim-Song, 2017)**
Schéma FHE conçu pour effectuer des calculs approchés sur des nombres réels
(contrairement à la plupart des autres schémas FHE, limités aux entiers).

**TenSEAL**
Bibliothèque Python développée par le projet OpenMined (organisation
reconnue en machine learning respectueux de la vie privée). Elle
n'implémente pas elle-même la cryptographie : c'est une surcouche Python
autour de Microsoft SEAL.

**Microsoft SEAL (Simple Encrypted Arithmetic Library)**
Bibliothèque C++ open source développée par Microsoft Research, une des
implémentations FHE les plus utilisées et citées au monde.

**Contexte**
Objet qui regroupe tous les paramètres cryptographiques (degré du polynôme,
taille des modules de coefficients, échelle globale) ainsi que les clés. Un
contexte peut être « complet » (avec clé secrète, côté client) ou « public »
(sans clé secrète, côté serveur).

**Degré du polynôme modulaire (`poly_modulus_degree`)**
Paramètre qui fixe le degré des polynômes utilisés en interne pour encoder
les données. Détermine à la fois le niveau de sécurité et le nombre de
valeurs pouvant être encodées dans un seul vecteur chiffré.

**Chaîne de modules de coefficients (`coeff_mod_bit_sizes`)**
Liste des tailles (en bits) de la chaîne de modules de coefficients.
Détermine combien de multiplications successives peuvent être effectuées
avant que le bruit ne devienne ingérable (« profondeur multiplicative »).

**Échelle globale (`global_scale`)**
Facteur d'échelle utilisé pour convertir les nombres réels en entiers avant
chiffrement, la cryptographie sous-jacente étant fondamentalement entière.

**Clés de Galois (Galois keys)**
Clés supplémentaires nécessaires pour effectuer certaines opérations sur des
vecteurs chiffrés (comme les rotations, utilisées en interne par les
produits scalaires). Générées côté client, incluses dans le contexte public
transmis au serveur.

**Sérialisation sans clé secrète**
Mécanisme permettant d'exporter un contexte sans sa clé secrète, pour le
transmettre en toute sécurité à un serveur qui doit pouvoir calculer sur les
données chiffrées mais jamais les déchiffrer.

**Vecteur chiffré**
Représentation d'un vecteur de nombres réels chiffré, supportant addition,
multiplication et produit scalaire directement entre vecteurs chiffrés ou
avec des vecteurs en clair.

**Erreur d'approximation**
Contrairement à un schéma exact comme Paillier, CKKS ne rend qu'une
approximation du résultat exact, à cause du bruit inhérent au schéma.

---

## 7. Cas d'usage : scoring bancaire chiffré

**Score (bancaire)**
Note calculée à partir de données financières d'un client (revenu, taux
d'endettement, nombre d'incidents de paiement) pour estimer un risque de
crédit.

**Variables du modèle**
Données d'entrée utilisées pour calculer le score : par exemple le revenu,
le taux d'endettement, le nombre d'incidents de paiement.

**Poids du modèle**
Coefficients appliqués à chaque variable pour calculer le score. Ce sont
des valeurs publiques, connues du serveur ; seules les données du client
doivent rester confidentielles.

**Biais**
Constante ajoutée au score après application des poids, équivalent de
l'ordonnée à l'origine d'un modèle linéaire.

---

## 8. Architecture technique

**API REST**
Interface de programmation permettant à une interface web (ou tout autre
client) de communiquer avec un serveur applicatif via des requêtes HTTP
structurées.

**FastAPI**
Framework web Python permettant d'exposer rapidement des API REST.

**Docker / conteneurisation**
Technologie permettant d'empaqueter une application avec toutes ses
dépendances dans un environnement isolé et reproductible, exécutable de la
même façon sur n'importe quelle machine.

**pytest**
Framework de tests automatisés pour Python.

**Isolation par sous-processus**
Technique consistant à exécuter un morceau de code potentiellement instable
(boucle infinie, crash) dans un processus séparé avec une limite de temps,
pour protéger l'application principale.

**Client / serveur**
Modèle d'architecture où le client (détenteur des données et de la clé
privée) envoie des données chiffrées à un serveur, qui effectue des calculs
sans jamais pouvoir les déchiffrer, puis renvoie un résultat chiffré que
seul le client peut lire.
