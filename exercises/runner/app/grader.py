"""Execute les tests pytest d'un exercice dans un sous-processus isole."""

import re
import subprocess
import sys
from pathlib import Path

TIMEOUT_SECONDS = 20

SUMMARY_RE = re.compile(
    r"(?P<counts>(?:\d+ \w+(?:, )?)+) in [\d.]+s"
)


def run_tests(exercise_dir: Path) -> dict:
    test_file = exercise_dir / "test_exercise.py"
    if not test_file.exists():
        return {
            "passed": False,
            "timed_out": False,
            "returncode": -1,
            "output": f"Fichier introuvable : {test_file}",
            "summary": "erreur interne",
        }

    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short", "--color=no"],
            cwd=str(exercise_dir),
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
        output = proc.stdout + "\n" + proc.stderr
        summary_match = SUMMARY_RE.search(output)
        summary = summary_match.group("counts") if summary_match else (
            "succes" if proc.returncode == 0 else "echec"
        )
        return {
            "passed": proc.returncode == 0,
            "timed_out": False,
            "returncode": proc.returncode,
            "output": output.strip(),
            "summary": summary,
        }
    except subprocess.TimeoutExpired:
        return {
            "passed": False,
            "timed_out": True,
            "returncode": None,
            "output": (
                f"Delai depasse ({TIMEOUT_SECONDS}s) : votre code contient probablement "
                "une boucle infinie ou un calcul beaucoup trop lent."
            ),
            "summary": "timeout",
        }
