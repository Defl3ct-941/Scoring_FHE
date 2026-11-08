# -*- mode: python ; coding: utf-8 -*-
"""Spécification PyInstaller de l'exécutable autonome fhecli.

Un seul fichier par OS, qui embarque l'interpréteur Python, fhecli, pytest,
cryptography et les données des exercices : l'étudiant n'a besoin d'aucune
installation de Python.

Le code est embarqué sous forme de bytecode compressé, jamais en source ;
les solutions restent encodées (.sol). Rien n'est donc lisible en clair dans
le binaire (vérifié par scripts/check_binary.py). C'est une dissuasion, pas
une protection contre un rétro-ingénieur déterminé.

Construction : python scripts/build_binary.py
"""

import platform
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules

ROOT = Path(SPECPATH).resolve().parent
sys.path.insert(0, str(ROOT))
from fhecli import __version__  # noqa: E402

SYSTEM = {"Windows": "windows", "Linux": "linux", "Darwin": "macos"}.get(platform.system(), platform.system().lower())
MACHINE = {"amd64": "x86_64", "x86_64": "x86_64", "arm64": "arm64", "aarch64": "arm64"}.get(
    platform.machine().lower(), platform.machine().lower())
NAME = f"fhe-cli-{__version__}-{SYSTEM}-{MACHINE}"

datas, binaries, hiddenimports = [], [], []
# pytest et cryptography sont nécessaires au code des étudiants exécuté par le
# binaire (sous-commande interne _run-pytest).
for package in ("pytest", "_pytest", "pluggy", "iniconfig", "packaging", "pygments", "cryptography"):
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(package)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden
# Bonus CKKS (ex10) : TenSEAL et numpy, embarqués quand ils sont installés
# (Python 3.11 à 3.14 ; absents sur Mac Intel, où l'ex10 est alors ignoré).
for package in ("tenseal", "numpy"):
    try:
        __import__(package)
    except ImportError:
        print(f"[fhecli.spec] {package} absent : non embarqué")
        continue
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(package)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden
if SYSTEM == "windows":
    hiddenimports += collect_submodules("colorama")
    # Les extensions à ABI stable (dont celle de cryptography) dépendent de
    # python3.dll et, depuis Python 3.15 (wheels « abi3t »), de python3t.dll,
    # livrée dans le sous-dossier abi3t-compat : PyInstaller ne les trouve pas
    # toujours d'elles-mêmes.
    for dll in (Path(sys.base_prefix) / "python3.dll",
                Path(sys.base_prefix) / "abi3t-compat" / "python3t.dll"):
        if dll.is_file():
            binaries.append((str(dll), "."))
hiddenimports += collect_submodules("fhecli")

# Données des exercices : liste, énoncés d'origine, solutions ENCODÉES.
# On n'ajoute PAS le dossier fhecli/ entier, pour ne jamais embarquer de source.
data_dir = ROOT / "fhecli" / "data"
for path in data_dir.rglob("*"):
    if path.is_file() and path.suffix in {".toml", ".py", ".sol"} and "__pycache__" not in path.parts:
        datas.append((str(path), str(Path("fhecli") / path.parent.relative_to(ROOT / "fhecli"))))

a = Analysis(
    [str(ROOT / "packaging" / "fhecli_entry.py")],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=["tkinter", "test", "unittest.test"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=NAME,
    console=True,
    upx=False,
    strip=False,
    runtime_tmpdir=None,
)
