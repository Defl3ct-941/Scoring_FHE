# Plan — Scoring financier sur données chiffrées via FHE : prototype et limites

## Problématique

Peut-on réaliser un scoring de crédit ou de risque directement sur des données chiffrées, sans jamais les exposer en clair, et est-ce réellement exploitable dans un contexte bancaire ou fintech aujourd'hui ?

---

## 1. Introduction

Contexte : scoring de crédit, enjeux RGPD, souveraineté des données.  
Aujourd'hui, calculer un score de risque oblige à accéder aux données brutes du client, revenus, historique, comportements. Le FHE permet en théorie de contourner ça.  
Présentation de la question centrale et des limites que l'on cherche à évaluer.

---

## 2. Ce qu'est le FHE (et ce que ce n'est pas)

Rappels cryptographiques : chiffrement classique, chiffrement partiellement homomorphique (Paillier), et FHE.  
Les schémas modernes : BFV, BGV, CKKS (pour les réels), TFHE.  
Le concept de bootstrapping et pourquoi c'est le verrou principal.  
Objectif : donner les bases sans entrer dans les démonstrations mathématiques.

---

## 3. Le scoring financier : ce qu'il faut calculer

Qu'est-ce qu'un score de crédit ? (score linéaire pondéré, régression logistique simplifiée)  
Quelles opérations mathématiques sont nécessaires : sommes, multiplications, éventuellement fonctions non-linéaires.  
Cette partie pose le problème côté "métier" et justifie le choix des schémas FHE utilisables.

---

## 4. FHE pour le scoring : état de l'art

Travaux académiques sur le scoring ou la régression logistique chiffrée.  
Ce que font les acteurs industriels (Zama, Microsoft SEAL, OpenFHE, IBM HElib).  
Cas d'usage proches dans la finance (détection de fraude, modèles fédérés).  
Montrer ce qui existe déjà et ce qui reste ouvert.

---

## 5. Prototype

Scénario : un client chiffre ses données (revenu, ratio d'endettement, incidents passés), envoie les chiffrés à un serveur qui calcule le score sans voir les valeurs, et renvoie le résultat chiffré.  
Choix de l'outil (à valider entre nous) : CKKS/SEAL pour la richesse arithmétique, ou Concrete de Zama pour un prototype plus accessible.
Implémentation du modèle : score linéaire pondéré dans un premier temps, régression logistique simplifiée si le temps le permet.
Métriques observées : temps de calcul, taille des données chiffrées, précision des résultats.

---

## 6. Limites et regard critique

Surcoût computationnel : ordres de grandeur vs calcul en clair.  
Expansion des données chiffrées.  
Complexité de mise en œuvre et paramétrage (choix des paramètres de sécurité, gestion des clés).  
Comparaison avec d'autres approches : MPC, differential privacy, TEE.  
Maturité réelle pour un déploiement bancaire.

---

## 7. Conclusion et perspectives

Ce que le FHE apporte vraiment au scoring financier aujourd'hui.  
Les conditions pour qu'il soit déployable à grande échelle : hardware dédié, standardisation, cas d'usage ciblés.  
Pistes d'évolution : accélération matérielle (GPU/FPGA), progrès sur le bootstrapping, émergence de standards (NIST, HomomorphicEncryption.org).

---
