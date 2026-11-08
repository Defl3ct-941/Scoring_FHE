"""Régénère les solutions encodées embarquées dans le paquet.

Lit les solutions en clair de solutions_src/*.py (gardées dans le dépôt, mais
exclues de la wheel et du sdist) et écrit fhecli/data/solutions/*.sol.

À relancer après toute modification d'une solution :
    python scripts/encode_solutions.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fhecli.solutions import decode, encode  # noqa: E402

SRC = ROOT / "solutions_src"
DST = ROOT / "fhecli" / "data" / "solutions"


def main() -> int:
    DST.mkdir(parents=True, exist_ok=True)
    sources = sorted(SRC.glob("*.py"))
    for src in sources:
        text = src.read_text(encoding="utf-8")
        blob = encode(text)
        assert decode(blob) == text
        (DST / f"{src.stem}.sol").write_text(blob, encoding="ascii", newline="\n")
        print(f"{src.name} -> {DST.relative_to(ROOT) / (src.stem + '.sol')}")
    stale = {p.stem for p in DST.glob("*.sol")} - {p.stem for p in sources}
    for name in sorted(stale):
        (DST / f"{name}.sol").unlink()
        print(f"supprimé (plus de source) : {name}.sol")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
