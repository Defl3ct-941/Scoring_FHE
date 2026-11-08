"""Vérifie un exécutable autonome fhecli : parcours étudiant complet, puis
absence de texte lisible (sources, solutions, énoncés) dans le binaire.

    python scripts/check_binary.py dist/fhe-cli-<version>-<os>-<arch>[.exe]

Le binaire est lancé avec un PATH réduit (sans Python), pour prouver qu'il
est autonome. Code de sortie 0 si tout est conforme.
"""

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fhecli import __version__, resources  # noqa: E402
from fhecli.info import exercise_names  # noqa: E402

FAILURES: list[str] = []


def check(condition: bool, label: str) -> None:
    print(("  OK    " if condition else "  ÉCHEC ") + label)
    if not condition:
        FAILURES.append(label)


def minimal_env() -> dict:
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith("PYTHON")}
    if os.name == "nt":
        root = os.environ.get("SystemRoot", r"C:\Windows")
        env["PATH"] = os.pathsep.join([rf"{root}\System32", root])
    else:
        env["PATH"] = "/usr/sbin:/usr/bin:/sbin:/bin"
    env["NO_COLOR"] = "1"
    return env


def run(binary: Path, *args: str, cwd: Path, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([str(binary), *args], cwd=cwd, env=minimal_env(), capture_output=True,
                          text=True, encoding="utf-8", errors="replace", input=stdin,
                          stdin=None if stdin is not None else subprocess.DEVNULL, timeout=300)


def solved_text(name: str, keep_marker: bool = False) -> str:
    original = resources.original_text(name)
    tests_start = original.rfind("\n# ----", 0, original.index("# Tests"))
    imports = "\n".join(line for line in original.splitlines() if re.match(r"^(import|from) ", line))
    marker = "\n# I AM NOT DONE\n" if keep_marker else "\n"
    return (f'"""ok"""\n{marker}\n{imports}\n\n{resources.solution_text(name)}\n'
            f"{original[tests_start:]}")


def scenario(binary: Path) -> None:
    names = exercise_names()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        print("Parcours étudiant (PATH sans Python) :")
        result = run(binary, "--version", cwd=tmp)
        check(result.stdout.strip() == f"fhe-cli {__version__}", f"--version -> {result.stdout.strip()}")
        check(run(binary, "list", cwd=tmp).returncode == 1, "list hors espace de travail -> 1")
        check(run(binary, "init", cwd=tmp).returncode == 0, "init")
        ws = tmp / "fhe-exercices"
        check(run(binary, "init", cwd=tmp).returncode == 1, "init refuse un espace existant")
        check("0/10" in run(binary, "list", cwd=ws).stdout, "list initial 0/10")
        check(run(binary, "run", names[0], cwd=ws).returncode == 1, "run sur l'énoncé -> 1")
        check(run(binary, "solution", names[0], cwd=ws).returncode == 1, "solution verrouillée -> 1")
        for name in names:
            path = ws / "exercises" / f"{name}.py"
            path.write_text(solved_text(name, keep_marker=True), encoding="utf-8")
            check(run(binary, "run", name, cwd=ws).returncode == 2, f"{name} : marqueur présent -> 2")
            path.write_text(solved_text(name), encoding="utf-8")
            result = run(binary, "run", name, cwd=ws)
            check(result.returncode == 0, f"{name} : résolu -> 0")
            if result.returncode != 0:
                print(result.stdout[-2000:], result.stderr[-2000:])
        check("10/10" in run(binary, "list", cwd=ws / "exercises").stdout, "list 10/10 (depuis un sous-dossier)")
        result = run(binary, "solution", names[0], cwd=ws)
        check(result.returncode == 0 and "def " in result.stdout, "solution débloquée")
        check(run(binary, "reset", "--all", cwd=ws, stdin="").returncode == 0
              and "10/10" in run(binary, "list", cwd=ws).stdout, "reset --all + EOF : annulé")
        check(run(binary, "reset", "--all", "-y", cwd=ws).returncode == 0
              and "0/10" in run(binary, "list", cwd=ws).stdout, "reset --all -y")


def plaintext_scan(binary: Path) -> None:
    print("Recherche de texte lisible dans le binaire :")
    blob = binary.read_bytes()
    needles: dict[str, str] = {}
    for src in sorted((ROOT / "solutions_src").glob("*.py")):
        for line in src.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if len(line) >= 24 and not line.startswith(("from ", "import ", '"""')):
                needles[f"solution {src.stem} : {line[:50]}"] = line
    for name in exercise_names():
        first_line = resources.original_text(name).splitlines()[1].strip()
        needles[f"énoncé {name} : {first_line}"] = first_line
    for module in sorted((ROOT / "fhecli").glob("*.py")):
        for line in module.read_text(encoding="utf-8").splitlines():
            if line.startswith("def ") and len(line) >= 24:
                needles[f"source {module.name} : {line[:50]}"] = line
                break
    for label, text in needles.items():
        visible = any(text.encode(enc) in blob for enc in ("utf-8", "utf-16-le"))
        check(not visible, f"absent en clair : {label}")


def main() -> int:
    binary = Path(sys.argv[1]).resolve()
    scenario(binary)
    plaintext_scan(binary)
    print()
    if FAILURES:
        print(f"{len(FAILURES)} vérification(s) en échec.")
        return 1
    print("Binaire conforme.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
