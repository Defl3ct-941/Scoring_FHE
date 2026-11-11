"""Vérification d'un exercice : tests cachés exécutés dans un sous-processus isolé."""

import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from fhecli import resources

MARKER = "I AM NOT DONE"
TIMEOUT_SECONDS = 20

# Sous-commande interne : dans un exécutable PyInstaller, sys.executable est
# le binaire fhecli lui-même (il n'y a pas forcément de Python installé sur la
# machine). Le binaire se relance donc avec cette sous-commande, qui exécute le
# pytest embarqué.
PYTEST_SUBCOMMAND = "_run-pytest"


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def has_marker(path: Path) -> bool:
    try:
        return MARKER in path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return True


# En-tête ajouté aux vérifications décodées : charge le fichier de l'étudiant
# (chemin passé par FHECLI_EXERCISE) et expose ses noms aux tests, comme si
# ceux-ci étaient écrits à la fin du fichier.
CHECK_PRELUDE = """\
import importlib.util as _ilu
import os as _os
import sys as _sys

_spec = _ilu.spec_from_file_location("exercice", _os.environ["FHECLI_EXERCISE"])
_module = _ilu.module_from_spec(_spec)
_sys.modules["exercice"] = _module
try:
    _spec.loader.exec_module(_module)
except BaseException as _error:  # erreur de syntaxe, import manquant...
    import traceback as _tb

    import pytest as _pytest

    _frames = [f for f in _tb.extract_tb(_error.__traceback__)
               if f.filename == _os.environ["FHECLI_EXERCISE"]]
    _pytest.exit("FHECLI-LOAD-ERROR\\n" + "".join(_tb.format_list(_frames))
                 + "".join(_tb.format_exception_only(_error)), returncode=1)
globals().update({k: v for k, v in vars(_module).items()
                  if not k.startswith("__") and not k.startswith("test")})
del _ilu, _os, _sys, _spec

"""
CHECK_PYTEST_INI = "[pytest]\naddopts = -p no:cacheprovider\n"
CHECK_LABEL = "<vérifications>"
LOAD_ERROR = "FHECLI-LOAD-ERROR"
RESULT_LINE = re.compile(r"::(test_\w+)(?:\[[^\]]*\])? (PASSED|FAILED|SKIPPED|ERROR|XFAIL|XPASS)")


@dataclass
class TestReport:
    passed: bool
    output: str
    results: list[tuple[str, str]] = field(default_factory=list)  # (test, PASSED/FAILED...)


def pytest_command(test_file: Path) -> list[str]:
    args = [str(test_file), "-v", "--tb=line", "--color=no", "-p", "no:cacheprovider"]
    if is_frozen():
        return [sys.executable, PYTEST_SUBCOMMAND, *args]
    return [sys.executable, "-m", "pytest", *args]


def check_exercise(path: Path) -> TestReport:
    """Lance les vérifications cachées d'un exercice sur le fichier de l'étudiant.

    Les vérifications sont embarquées encodées dans le paquet (jamais dans le
    fichier que l'étudiant édite). Elles sont décodées dans un dossier
    temporaire le temps de l'exécution de pytest, puis effacées. Un timeout
    est traité comme un échec (boucle infinie possible dans le code de
    l'exercice).
    """
    name = path.stem
    if not path.exists():
        return TestReport(False, f"Fichier introuvable : {path}\nRecréez-le avec : fhe-cli reset {name}")
    if not resources.has_check(name):
        return TestReport(False, f"Aucune vérification disponible pour {name}.")
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1",
           "PYTHONDONTWRITEBYTECODE": "1", "FHECLI_EXERCISE": str(path.resolve())}
    if is_frozen():
        env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    tmp = Path(tempfile.mkdtemp(prefix="fhecli-"))
    try:
        test_file = tmp / f"verif_{name}.py"
        test_file.write_text(CHECK_PRELUDE + resources.check_text(name), encoding="utf-8")
        (tmp / "pytest.ini").write_text(CHECK_PYTEST_INI, encoding="utf-8")
        try:
            result = subprocess.run(
                pytest_command(test_file),
                cwd=tmp,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                timeout=TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            return TestReport(False, f"Délai dépassé ({TIMEOUT_SECONDS} s) : boucle infinie possible ?")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    output = _clean_output(result.stdout + result.stderr, tmp, test_file)
    if LOAD_ERROR in output:
        kept = []
        for line in output.split(LOAD_ERROR, 1)[1].splitlines():
            if line.startswith(("!!!", "===", "ERROR ", "___")):
                break
            kept.append(line[4:] if line.startswith("    ") else line)
        message = "\n".join(kept)
        return TestReport(False, "Votre fichier ne peut pas être chargé :\n" + message.strip())
    results = RESULT_LINE.findall(output)
    return TestReport(result.returncode == 0, output, results)


def _clean_output(output: str, tmp: Path, test_file: Path) -> str:
    """Masque les chemins temporaires et l'en-tête de pytest."""
    for text in (str(test_file), str(tmp)):
        output = output.replace(text, CHECK_LABEL)
    output = output.replace(test_file.name, CHECK_LABEL)
    kept = [line for line in output.splitlines()
            if not line.startswith(("platform ", "cachedir:", "rootdir:", "configfile:", "plugins:",
                                    "collecting ...", "cachedir"))
            and "test session starts" not in line]
    return "\n".join(kept).strip()


def run_tests(path: Path) -> tuple[bool, str]:
    """Compatibilité : (succès, sortie_texte) des vérifications d'un exercice."""
    report = check_exercise(path)
    return report.passed, report.output


def status(path: Path) -> str:
    """Classe un exercice en 'done', 'almost' ou 'pending'."""
    passed, _ = run_tests(path)
    if not passed:
        return "pending"
    if has_marker(path):
        return "almost"
    return "done"
