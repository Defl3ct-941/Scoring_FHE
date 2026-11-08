# Prérequis système de fhe-cli

## Installation avec pip (`pip install fhe-cli`)

| Fonctionnalité | Python | Plateformes | Installé automatiquement |
|---|---|---|---|
| Atelier de base : chiffrement classique, Paillier, scoring (ex1 à ex9) | 3.11 ou plus récent | Windows, Linux, macOS (Intel et Apple Silicon) | `cryptography`, `pytest` |
| Bonus CKKS (ex10, TenSEAL) | 3.11 à 3.14 | Windows x86_64 ; Linux x86_64 et aarch64 (glibc 2.28+ ou musl) ; macOS 14+ sur Apple Silicon | `tenseal`, `numpy` |

TenSEAL 0.3.18 ne publie pas de version précompilée pour **Python 3.15**, les
**Mac Intel** ni **macOS 11 à 13**. Sur ces configurations, `pip install fhe-cli`
fonctionne quand même : TenSEAL n'est simplement pas installé et seul l'ex10
est ignoré (marqué « skipped »). Pour le faire, utilisez Python 3.14 ou
l'exécutable autonome.

Autres besoins : environ 150 Mo d'espace disque, un accès réseau pendant
l'installation, un terminal (PowerShell, cmd, Terminal macOS, shell Linux).

## Exécutables autonomes (sans Python)

Un fichier par système, qui embarque Python, `fhe-cli`, pytest, cryptography,
TenSEAL et les exercices : aucune installation n'est nécessaire.

| Système | Fichier | CKKS (ex10) |
|---|---|---|
| Windows 10 / 11, 64 bits | `fhe-cli-<version>-windows-x86_64.exe` | oui |
| Linux x86_64, glibc 2.35+ (Ubuntu 22.04, Debian 12 ou plus récent) | `fhe-cli-<version>-linux-x86_64` | oui |
| macOS 14+ sur Apple Silicon | `fhe-cli-<version>-macos-arm64` | oui |
| macOS sur Mac Intel | `fhe-cli-<version>-macos-x86_64` | non (ex10 ignoré) |

Taille : 40 à 50 Mo. Sous macOS, le binaire n'est pas signé : autorisez-le au
premier lancement dans Réglages système > Confidentialité et sécurité.
