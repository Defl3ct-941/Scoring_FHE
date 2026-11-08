"""Construit l'exécutable autonome fhe-cli pour l'OS courant (PyInstaller).

PyInstaller ne fait pas de compilation croisée : lancez ce script sur chaque
OS (c'est ce que fait la CI GitHub Actions), avec un venv où sont installés
le paquet (pip install -e .) et PyInstaller :

    pip install -e . pyinstaller
    python scripts/build_binary.py

Le binaire est écrit dans dist/ (fhe-cli-<version>-<os>-<arch>[.exe]), puis
vérifié par scripts/check_binary.py.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
         "--distpath", str(ROOT / "dist"), "--workpath", str(ROOT / "build"),
         str(ROOT / "packaging" / "fhecli.spec")],
        check=True,
    )
    built = sorted((ROOT / "dist").glob("fhe-cli-*"), key=lambda p: p.stat().st_mtime)
    if not built:
        print("Aucun binaire produit.", file=sys.stderr)
        return 1
    binary = built[-1]
    print(f"Binaire : {binary} ({binary.stat().st_size / 1e6:.1f} Mo)")
    return subprocess.run([sys.executable, str(ROOT / "scripts" / "check_binary.py"), str(binary)]).returncode


if __name__ == "__main__":
    raise SystemExit(main())
