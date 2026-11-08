"""Execution des tests d'un exercice, dans un sous-processus isole."""

import subprocess
import sys
from pathlib import Path

MARKER = "I AM NOT DONE"
TIMEOUT_SECONDS = 20


def has_marker(path: Path) -> bool:
    try:
        return MARKER in path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return True


def run_tests(path: Path) -> tuple[bool, str]:
    """Lance `pytest` sur ce fichier (implementation + tests embarques).

    Renvoie (succes, sortie_texte). Un timeout ou une exception du
    sous-processus sont traites comme un echec, pas comme une erreur fatale
    de l'outil (boucle infinie possible dans le code de l'exercice).
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(path), "-q", "--tb=short", "--color=no"],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
        return result.returncode == 0, (result.stdout + result.stderr).strip()
    except subprocess.TimeoutExpired:
        return False, f"Timeout depasse ({TIMEOUT_SECONDS}s) : boucle infinie possible ?"


def status(path: Path) -> str:
    """Classe un exercice en 'done', 'almost' ou 'pending'."""
    passed, _ = run_tests(path)
    if not passed:
        return "pending"
    if has_marker(path):
        return "almost"
    return "done"
