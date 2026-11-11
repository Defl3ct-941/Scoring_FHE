"""Tests automatisés de l'outil fhe-cli (et non des exercices eux-mêmes).

Lancement, depuis le dossier fhe-exercices-cli :
    python -m pytest tests -q

Chaque test travaille dans un espace de travail temporaire créé par
`fhe-cli init` : rien n'est modifié dans le dépôt.
"""

import hashlib
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest

CLI_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CLI_ROOT))

from fhecli import __version__, resources, solutions  # noqa: E402
from fhecli.info import exercise_names  # noqa: E402

NAMES = exercise_names()
MARKER_LINE = "# I AM NOT DONE"


def fhecli(*args, cwd, input=None, env_extra=None):
    env = {**os.environ, "PYTHONPATH": str(CLI_ROOT), "NO_COLOR": "1", **(env_extra or {})}
    kwargs = {"input": input} if input is not None else {"stdin": subprocess.DEVNULL}
    return subprocess.run(
        [sys.executable, "-m", "fhecli", *args],
        cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=env, timeout=120, **kwargs,
    )


def solved_text(name: str, keep_marker: bool = False) -> str:
    """Énoncé d'origine dont les fonctions sont remplacées par la solution."""
    original = resources.original_text(name)
    imports = "\n".join(line for line in original.splitlines() if re.match(r"^(import|from) ", line))
    marker = f"\n{MARKER_LINE}\n" if keep_marker else "\n"
    return f'"""{name} résolu."""\n{marker}\n{imports}\n\n{resources.solution_text(name)}\n'


def solve(ws: Path, name: str, keep_marker: bool = False) -> None:
    (ws / "exercises" / f"{name}.py").write_text(solved_text(name, keep_marker), encoding="utf-8")


@pytest.fixture
def ws(tmp_path):
    result = fhecli("init", "ws", cwd=tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    return tmp_path / "ws"


# --- Paquet et données ----------------------------------------------------

def test_version():
    result = fhecli("--version", cwd=CLI_ROOT)
    assert result.returncode == 0
    assert result.stdout.strip() == f"fhe-cli {__version__}"


def test_solutions_are_encoded_and_decode():
    for name in NAMES:
        blob = (CLI_ROOT / "fhecli" / "data" / "solutions" / f"{name}.sol").read_text(encoding="ascii")
        assert blob.startswith(solutions.HEADER)
        assert "def " not in blob  # aucun code en clair
        assert "def " in resources.solution_text(name)


def test_encoded_solutions_match_sources():
    src = CLI_ROOT / "solutions_src"
    if not src.is_dir():
        pytest.skip("solutions_src/ absent (sdist)")
    for name in NAMES:
        assert resources.solution_text(name) == (src / f"{name}.py").read_text(encoding="utf-8"), (
            f"{name}.sol est périmé : relancez python scripts/encode_solutions.py")


def test_checks_are_encoded_and_hidden_from_students():
    """Les vérifications ne sont jamais dans le fichier que l'étudiant édite."""
    for name in NAMES:
        blob = (CLI_ROOT / "fhecli" / "data" / "checks" / f"{name}.chk").read_text(encoding="ascii")
        assert blob.startswith(solutions.CHECK_HEADER)
        assert "def test_" not in blob
        assert "def test_" in resources.check_text(name)
        original = resources.original_text(name)
        assert "def test_" not in original and "# Tests" not in original


def test_encoded_checks_match_sources():
    src = CLI_ROOT / "checks_src"
    if not src.is_dir():
        pytest.skip("checks_src/ absent (sdist)")
    for name in NAMES:
        assert resources.check_text(name) == (src / f"{name}.py").read_text(encoding="utf-8"), (
            f"{name}.chk est périmé : relancez python scripts/encode_solutions.py")


def test_encode_decode_roundtrip():
    text = "def f():\n    return 'éàç €'\n"
    assert solutions.decode(solutions.encode(text)) == text
    with pytest.raises(ValueError):
        solutions.decode("pas une solution")


def test_hint_ex1_has_accents():
    assert "« é »" in resources.info_text()


# --- init ------------------------------------------------------------------

def test_init_creates_workspace(ws):
    assert (ws / "fhecli.toml").is_file()
    assert not (ws / "pytest.ini").exists()
    for name in NAMES:
        assert (ws / "exercises" / f"{name}.py").read_text(encoding="utf-8") == resources.original_text(name)


def test_init_default_directory(tmp_path):
    result = fhecli("init", cwd=tmp_path)
    assert result.returncode == 0
    assert (tmp_path / "fhe-exercices" / "fhecli.toml").is_file()


def test_init_refuses_existing_workspace(ws):
    path = ws / "exercises" / f"{NAMES[0]}.py"
    modified = path.read_text(encoding="utf-8") + "# modifié\n"
    path.write_text(modified, encoding="utf-8")
    result = fhecli("init", "ws", cwd=ws.parent)
    assert result.returncode == 1
    assert "existe déjà" in result.stdout
    assert path.read_text(encoding="utf-8") == modified


def test_package_data_untouched(ws):
    data = CLI_ROOT / "fhecli" / "data"

    def digest():
        return {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in data.rglob("*") if p.is_file()}

    before = digest()
    solve(ws, NAMES[0])
    fhecli("run", NAMES[0], cwd=ws)
    fhecli("reset", "--all", "-y", cwd=ws)
    assert digest() == before


# --- Sans espace de travail -----------------------------------------------

@pytest.mark.parametrize("args", [["list"], ["run", "ex1_cesar"], ["check", "ex1"], ["check"], ["hint", "ex1_cesar"],
                                  ["solution", "ex1_cesar"], ["reset", "--all", "-y"], ["watch"]])
def test_commands_need_workspace(tmp_path, args):
    result = fhecli(*args, cwd=tmp_path)
    assert result.returncode == 1
    assert "fhe-cli init" in result.stdout


def test_workspace_found_from_subdirectory(ws):
    result = fhecli("list", cwd=ws / "exercises")
    assert result.returncode == 0
    assert "Progression : 0/10" in result.stdout


# --- list / run / marqueur -------------------------------------------------

def test_list_initial(ws):
    result = fhecli("list", cwd=ws)
    assert result.returncode == 0
    assert "Progression : 0/10 exercices résolus." in result.stdout
    assert "César" in result.stdout


def test_run_statement_fails(ws):
    result = fhecli("run", NAMES[0], cwd=ws)
    assert result.returncode == 1
    assert "Des tests échouent encore." in result.stdout


@pytest.mark.parametrize("name", NAMES)
def test_marker_then_done(ws, name):
    solve(ws, name, keep_marker=True)
    result = fhecli("run", name, cwd=ws)
    assert result.returncode == 2
    assert "I AM NOT DONE" in result.stdout
    assert "[~]" in fhecli("list", cwd=ws).stdout

    solve(ws, name, keep_marker=False)
    result = fhecli("run", name, cwd=ws)
    assert result.returncode == 0
    assert "Tous les tests passent." in result.stdout


def test_all_solved(ws):
    for name in NAMES:
        solve(ws, name)
    assert "Progression : 10/10 exercices résolus." in fhecli("list", cwd=ws).stdout


def test_syntax_error_and_missing_file(ws):
    path = ws / "exercises" / f"{NAMES[0]}.py"
    path.write_text(path.read_text(encoding="utf-8") + "\ndef oups(:\n", encoding="utf-8")
    result = fhecli("run", NAMES[0], cwd=ws)
    assert result.returncode == 1 and "SyntaxError" in result.stdout
    path.unlink()
    result = fhecli("run", NAMES[0], cwd=ws)
    assert result.returncode == 1 and "introuvable" in result.stdout
    assert "Traceback" not in result.stdout + result.stderr


# --- solution verrouillée ---------------------------------------------------

def test_solution_locked_then_unlocked(ws):
    name = NAMES[0]
    locked = fhecli("solution", name, cwd=ws)
    assert locked.returncode == 1
    assert "verrouillée" in locked.stdout
    assert "def caesar_encrypt" not in locked.stdout

    solve(ws, name, keep_marker=True)
    still_locked = fhecli("solution", name, cwd=ws)
    assert still_locked.returncode == 1 and "verrouillée" in still_locked.stdout

    solve(ws, name)
    unlocked = fhecli("solution", name, cwd=ws)
    assert unlocked.returncode == 0
    assert "def caesar_encrypt" in unlocked.stdout


# --- reset ------------------------------------------------------------------

@pytest.mark.parametrize("answer", ["n\n", "\n", ""])  # non, Entrée seule, EOF
def test_reset_refused(ws, answer):
    name = NAMES[0]
    solve(ws, name)
    result = fhecli("reset", name, cwd=ws, input=answer)
    assert result.returncode == 0
    assert "Annulé" in result.stdout
    assert "Traceback" not in result.stderr
    assert (ws / "exercises" / f"{name}.py").read_text(encoding="utf-8") == solved_text(name)


@pytest.mark.parametrize("answer", ["o\n", "oui\n", "y\n", "YES\n"])
def test_reset_confirmed(ws, answer):
    name = NAMES[1]
    solve(ws, name)
    result = fhecli("reset", name, cwd=ws, input=answer)
    assert result.returncode == 0
    assert (ws / "exercises" / f"{name}.py").read_text(encoding="utf-8") == resources.original_text(name)


def test_reset_all_needs_confirmation_or_yes_flag(ws):
    for name in NAMES:
        solve(ws, name)
    assert fhecli("reset", "--all", cwd=ws, input="").returncode == 0  # EOF : annulé
    assert "10/10" in fhecli("list", cwd=ws).stdout
    result = fhecli("reset", "--all", "-y", cwd=ws)
    assert result.returncode == 0
    for name in NAMES:
        assert (ws / "exercises" / f"{name}.py").read_text(encoding="utf-8") == resources.original_text(name)


def test_reset_recreates_deleted_file(ws):
    path = ws / "exercises" / f"{NAMES[2]}.py"
    path.unlink()
    assert fhecli("reset", NAMES[2], "-y", cwd=ws).returncode == 0
    assert path.read_text(encoding="utf-8") == resources.original_text(NAMES[2])


def test_reset_without_name(ws):
    result = fhecli("reset", cwd=ws)
    assert result.returncode == 1 and "--all" in result.stdout


# --- erreurs ----------------------------------------------------------------

@pytest.mark.parametrize("command", ["run", "check", "hint", "solution", "reset"])
def test_unknown_exercise(ws, command):
    result = fhecli(command, "ex99_inconnu", cwd=ws)
    assert result.returncode == 1
    assert "Exercice inconnu" in result.stdout


def test_unknown_command(ws):
    result = fhecli("foo", cwd=ws)
    assert result.returncode == 2
    assert "foo" in result.stderr


def test_utf8_output_with_legacy_encoding(ws):
    result = subprocess.run(
        [sys.executable, "-m", "fhecli", "hint", NAMES[0]], cwd=ws, capture_output=True,
        env={**os.environ, "PYTHONPATH": str(CLI_ROOT), "PYTHONIOENCODING": "cp1252", "PYTHONUTF8": "0"},
    )
    assert result.returncode == 0
    assert "« é »".encode("utf-8") in result.stdout


# --- check et alias --------------------------------------------------------

def test_check_statement_fails_without_revealing_checks(ws):
    result = fhecli("check", "ex1", cwd=ws)
    assert result.returncode == 1
    assert "0/7 vérifications réussies" in result.stdout
    assert "[xx] known vector" in result.stdout
    assert "def test_" not in result.stdout
    assert "fhecli-" not in result.stdout  # dossier temporaire masqué


@pytest.mark.parametrize("name", NAMES)
def test_check_marker_then_done(ws, name):
    alias = name.split("_")[0]
    solve(ws, name, keep_marker=True)
    result = fhecli("check", alias, cwd=ws)
    assert result.returncode == 2, result.stdout
    assert "I AM NOT DONE" in result.stdout
    solve(ws, name)
    result = fhecli("check", alias, cwd=ws)
    assert result.returncode == 0, result.stdout
    assert "résolu" in result.stdout and "[xx]" not in result.stdout


def test_check_partial_progress(ws):
    path = ws / "exercises" / "ex1_cesar.py"
    path.write_text(solved_text("ex1_cesar").replace("% 26", "% 25"), encoding="utf-8")
    result = fhecli("check", "1", cwd=ws)
    assert result.returncode == 1
    assert "[ok]" in result.stdout and "[xx]" in result.stdout
    assert "AssertionError" in result.stdout


def test_check_without_argument_uses_next_exercise(ws):
    solve(ws, NAMES[0])
    result = fhecli("check", cwd=ws)
    assert result.returncode == 1 and f"Vérification de {NAMES[1]}" in result.stdout
    for name in NAMES:
        solve(ws, name)
    result = fhecli("check", cwd=ws)
    assert result.returncode == 0 and "Tous les exercices sont résolus" in result.stdout


def test_check_all(ws):
    solve(ws, NAMES[0])
    result = fhecli("check", "--all", cwd=ws)
    assert result.returncode == 1
    assert "Progression : 1/10 exercices résolus." in result.stdout
    assert "7/7" in result.stdout


def test_check_reports_load_errors_briefly(ws):
    path = ws / "exercises" / f"{NAMES[0]}.py"
    path.write_text("def oups(:\n", encoding="utf-8")
    result = fhecli("check", "ex1", cwd=ws)
    assert result.returncode == 1
    assert "SyntaxError" in result.stdout and "ne peut pas être chargé" in result.stdout
    assert "_pytest" not in result.stdout


@pytest.mark.parametrize("alias", ["ex1", "exo1", "1", "EX1", "ex1_cesar.py"])
def test_exercise_aliases(ws, alias):
    for command in ("run", "hint", "solution"):
        result = fhecli(command, alias, cwd=ws)
        assert "Exercice inconnu" not in result.stdout, (command, alias)
    assert "César" in fhecli("check", alias, cwd=ws).stdout


def test_alias_ex10_is_not_ex1(ws):
    result = fhecli("check", "ex10", cwd=ws)
    assert "ex10_ckks_bonus" in result.stdout


def test_list_shows_aliases(ws):
    out = fhecli("list", cwd=ws).stdout
    assert "ex1   ex1_cesar" in out and "ex10  ex10_ckks_bonus" in out


# --- watch --------------------------------------------------------------------

def test_watch_advances_and_finishes(ws):
    env = {**os.environ, "PYTHONPATH": str(CLI_ROOT), "NO_COLOR": "1", "PYTHONUNBUFFERED": "1"}
    log = ws / "watch.log"
    with log.open("w", encoding="utf-8") as out:
        proc = subprocess.Popen([sys.executable, "-m", "fhecli", "start"], cwd=ws, env=env,
                                stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT)
        try:
            time.sleep(4)
            for name in NAMES:
                solve(ws, name)
                time.sleep(5)
            proc.wait(timeout=60)
        finally:
            if proc.poll() is None:
                proc.kill()
    text = log.read_text(encoding="utf-8")
    # Les exercices déjà résolus quand watch y arrive sont sautés (comportement
    # voulu) : on vérifie seulement le départ et l'arrivée.
    assert f"Exercice 1/{len(NAMES)}" in text
    assert "Félicitations" in text
    assert proc.returncode == 0


# --- Exécutable autonome (PyInstaller) -------------------------------------

def test_pytest_command_normal_and_frozen(monkeypatch, tmp_path):
    from fhecli import runner

    target = tmp_path / "ex.py"
    monkeypatch.delattr(sys, "frozen", raising=False)
    assert runner.pytest_command(target)[:3] == [sys.executable, "-m", "pytest"]
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    assert runner.pytest_command(target)[:2] == [sys.executable, runner.PYTEST_SUBCOMMAND]


def test_internal_pytest_subcommand(tmp_path):
    """`fhe-cli _run-pytest` exécute pytest : c'est ce qu'utilise le binaire."""
    (tmp_path / "verif_demo.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    result = fhecli("_run-pytest", "verif_demo.py", "-q", "-p", "no:cacheprovider", cwd=tmp_path)
    assert result.returncode == 0, result.stdout
    assert "1 passed" in result.stdout
    assert "_run-pytest" not in fhecli("--help", cwd=tmp_path).stdout


# --- Aide et noms de commandes ----------------------------------------------

COMMAND_NAMES = ["init", "start", "next", "previous", "list", "check", "run", "hint", "solution", "reset", "help"]


@pytest.mark.parametrize("args", [[], ["help"], ["-h"], ["--help"]])
def test_general_help_lists_all_commands(tmp_path, args):
    result = fhecli(*args, cwd=tmp_path)
    assert result.returncode == 0
    for name in COMMAND_NAMES:
        assert f"  {name}" in result.stdout, name
    assert "fhe-cli init" in result.stdout and "fhe-cli start" in result.stdout
    assert "usage:" not in result.stdout  # aide en français, pas celle d'argparse


@pytest.mark.parametrize("args", [["help", "run"], ["help", "check"], ["check", "-h"], ["run", "--help"], ["reset", "-h"], ["help", "watch"]])
def test_command_help(tmp_path, args):
    result = fhecli(*args, cwd=tmp_path)
    assert result.returncode == 0
    assert result.stdout.startswith("fhe-cli ")
    assert "usage:" not in result.stdout


def test_help_unknown_topic(tmp_path):
    result = fhecli("help", "foo", cwd=tmp_path)
    assert result.returncode == 2 and "Commande inconnue" in result.stdout


def test_missing_argument_error_in_french(ws):
    result = fhecli("run", cwd=ws)
    assert result.returncode == 2
    assert "argument manquant" in result.stderr and "fhe-cli help" in result.stderr


def test_watch_is_an_alias_of_start(ws):
    for name in NAMES:
        solve(ws, name)
    for command in ("start", "watch"):
        result = fhecli(command, cwd=ws)
        assert result.returncode == 0 and "Félicitations" in result.stdout


# --- next / previous ----------------------------------------------------------

def test_next_picks_first_unsolved(ws):
    result = fhecli("next", cwd=ws)
    assert result.returncode == 1  # énoncé non résolu : les tests échouent
    assert f"{NAMES[0]} - " in result.stdout and "(1/10)" in result.stdout
    solve(ws, NAMES[0])
    solve(ws, NAMES[1])
    result = fhecli("next", cwd=ws)
    assert f"{NAMES[2]} - " in result.stdout and "(3/10)" in result.stdout


def test_next_when_everything_is_solved(ws):
    for name in NAMES:
        solve(ws, name)
    result = fhecli("next", cwd=ws)
    assert result.returncode == 0 and "Félicitations" in result.stdout


def test_previous(ws):
    result = fhecli("previous", cwd=ws)
    assert result.returncode == 0 and "Pas d'exercice précédent." in result.stdout
    solve(ws, NAMES[0])
    solve(ws, NAMES[1])
    result = fhecli("previous", cwd=ws)
    assert result.returncode == 0
    assert f"{NAMES[1]} - " in result.stdout and "Tous les tests passent." in result.stdout


def test_help_lists_next_and_previous(tmp_path):
    out = fhecli("help", cwd=tmp_path).stdout
    assert out.index("  start") < out.index("  next") < out.index("  previous") < out.index("  list")
    for topic in ("next", "previous"):
        detail = fhecli("help", topic, cwd=tmp_path)
        assert detail.returncode == 0 and detail.stdout.startswith(f"fhe-cli {topic}")


def test_messages_always_use_fhe_cli(ws, tmp_path):
    """Même lancée via l'alias, l'aide et les messages proposent `fhe-cli`."""
    out = fhecli("help", cwd=tmp_path).stdout
    assert "Alias disponibles : fhecli" in out
    commands_part = out.split("Alias disponibles")[0]
    assert "fhecli " not in commands_part
    for args in (["run", NAMES[0]], ["solution", NAMES[0]], ["init", "ws"]):
        text = fhecli(*args, cwd=ws if args[0] != "init" else ws.parent).stdout
        assert "fhecli " not in text and "fhe-cli " in text, args
