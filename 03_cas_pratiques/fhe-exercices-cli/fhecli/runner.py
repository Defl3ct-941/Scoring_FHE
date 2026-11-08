"""Exécution des tests d'un exercice, dans un sous-processus isolé."""

import os
import subprocess
import sys
from pathlib import Path

MARKER = "I AM NOT DONE"
TIMEOUT_SECONDS = 20


def has_marker(path: Path) -> bool:
    try:
        return MARKER in path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return True


def run_tests(path: Path) -> tuple[bool, str]:
    """Lance `pytest` sur ce fichier (implémentation + tests embarqués).

    Renvoie (succès, sortie_texte). Un timeout est traité comme un échec,
    pas comme une erreur fatale de l'outil (boucle infinie possible dans le
    code de l'exercice). pytest est lancé depuis l'espace de travail, pour
    qu'il y trouve le pytest.ini.
    """
    if not path.exists():
        return False, f"Fichier introuvable : {path}\nRecréez-le avec : fhecli reset {path.stem}"
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(path), "-q", "--tb=short", "--color=no"],
            cwd=path.parent.parent,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=TIMEOUT_SECONDS,
        )
        return result.returncode == 0, (result.stdout + result.stderr).strip()
    except subprocess.TimeoutExpired:
        return False, f"Délai dépassé ({TIMEOUT_SECONDS} s) : boucle infinie possible ?"


def status(path: Path) -> str:
    """Classe un exercice en 'done', 'almost' ou 'pending'."""
    passed, _ = run_tests(path)
    if not passed:
        return "pending"
    if has_marker(path):
        return "almost"
    return "done"
