"""Encodage des solutions de référence et des vérifications embarquées.

Les solutions (.sol) et les vérifications des exercices (.chk) ne sont pas
stockées en clair dans le paquet : elles sont
compressées (zlib) puis encodées en base64, derrière un petit en-tête.
C'est une simple DISSUASION (éviter qu'un étudiant tombe sur la correction en
ouvrant le dossier du paquet), PAS une protection cryptographique : n'importe
qui peut les décoder avec ce module.
"""

import base64
import zlib

HEADER = "FHECLI-SOLUTION/1"
CHECK_HEADER = "FHECLI-CHECK/1"
LINE_WIDTH = 76


def encode(text: str, header: str = HEADER) -> str:
    """Encode un texte en clair (format .sol, ou .chk avec CHECK_HEADER)."""
    payload = base64.b64encode(zlib.compress(text.encode("utf-8"), 9)).decode("ascii")
    lines = [payload[i:i + LINE_WIDTH] for i in range(0, len(payload), LINE_WIDTH)]
    return "\n".join([header, *lines]) + "\n"


def decode(blob: str, header: str = HEADER) -> str:
    """Décode un fichier produit par `encode` avec le même en-tête."""
    lines = blob.strip().splitlines()
    if not lines or lines[0].strip() != header:
        raise ValueError("Format de solution inconnu (en-tête manquant).")
    payload = "".join(line.strip() for line in lines[1:])
    return zlib.decompress(base64.b64decode(payload)).decode("utf-8")
