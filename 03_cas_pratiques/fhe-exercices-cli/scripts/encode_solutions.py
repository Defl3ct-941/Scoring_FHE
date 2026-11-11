"""Régénère les solutions et les vérifications encodées embarquées dans le paquet.

Lit les sources en clair, gardées dans le dépôt mais exclues de la wheel, du
sdist et des exécutables :
    solutions_src/*.py -> fhecli/data/solutions/*.sol  (solutions de référence)
    checks_src/*.py    -> fhecli/data/checks/*.chk     (vérifications des exercices)

À relancer après toute modification d'une solution ou d'une vérification :
    python scripts/encode_solutions.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fhecli.solutions import CHECK_HEADER, HEADER, decode, encode  # noqa: E402

TARGETS = [
    (ROOT / "solutions_src", ROOT / "fhecli" / "data" / "solutions", ".sol", HEADER),
    (ROOT / "checks_src", ROOT / "fhecli" / "data" / "checks", ".chk", CHECK_HEADER),
]


def encode_dir(src_dir: Path, dst_dir: Path, suffix: str, header: str) -> None:
    dst_dir.mkdir(parents=True, exist_ok=True)
    sources = sorted(src_dir.glob("*.py"))
    for src in sources:
        text = src.read_text(encoding="utf-8")
        blob = encode(text, header)
        assert decode(blob, header) == text
        (dst_dir / f"{src.stem}{suffix}").write_text(blob, encoding="ascii", newline="\n")
        print(f"{src.relative_to(ROOT)} -> {(dst_dir / (src.stem + suffix)).relative_to(ROOT)}")
    stale = {p.stem for p in dst_dir.glob(f"*{suffix}")} - {p.stem for p in sources}
    for name in sorted(stale):
        (dst_dir / f"{name}{suffix}").unlink()
        print(f"supprimé (plus de source) : {name}{suffix}")


def main() -> int:
    for target in TARGETS:
        encode_dir(*target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
