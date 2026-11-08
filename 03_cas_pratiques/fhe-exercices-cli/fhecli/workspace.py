"""Espace de travail de l'étudiant.

Un espace de travail est un dossier qui contient le fichier marqueur
`fhecli.toml`, un `pytest.ini` et le dossier `exercises/` où l'étudiant écrit
son code. Il est créé par `fhecli init` ; toutes les autres commandes le
retrouvent en remontant depuis le dossier courant jusqu'au marqueur.
"""

from pathlib import Path

from fhecli import __version__, resources

MARKER_FILE = "fhecli.toml"
EXERCISES_DIR = "exercises"
DEFAULT_DIR = "fhe-exercices"

MARKER_CONTENT = f"""\
# Espace de travail fhecli : ce fichier permet à `fhecli` de retrouver vos
# exercices depuis n'importe quel sous-dossier. Ne le supprimez pas.
[workspace]
created_with = "{__version__}"
"""

PYTEST_INI = """\
[pytest]
# Les exercices contiennent leurs propres tests : on collecte donc tous les
# fichiers .py du dossier exercises/ (pas seulement test_*.py).
python_files = *.py
testpaths = exercises
addopts = -p no:cacheprovider
"""


class WorkspaceNotFound(Exception):
    """Aucun espace de travail trouvé depuis le dossier courant."""


def find_workspace(start: Path | None = None) -> Path:
    """Remonte depuis `start` (ou le dossier courant) jusqu'au marqueur."""
    current = (start or Path.cwd()).resolve()
    for folder in (current, *current.parents):
        if (folder / MARKER_FILE).is_file():
            return folder
    raise WorkspaceNotFound(str(current))


def init_workspace(target: Path, exercise_names: list[str]) -> Path:
    """Crée un espace de travail neuf. Refuse d'écraser un espace existant."""
    target = target.resolve()
    if (target / MARKER_FILE).exists() or (target / EXERCISES_DIR).exists():
        raise FileExistsError(str(target))
    exercises = target / EXERCISES_DIR
    exercises.mkdir(parents=True)
    for name in exercise_names:
        (exercises / f"{name}.py").write_text(resources.original_text(name), encoding="utf-8")
    (target / "pytest.ini").write_text(PYTEST_INI, encoding="utf-8")
    (target / MARKER_FILE).write_text(MARKER_CONTENT, encoding="utf-8")
    return target
