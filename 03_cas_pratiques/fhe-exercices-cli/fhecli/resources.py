"""Accès aux données embarquées dans le paquet (lecture seule).

Les énoncés d'origine, la liste des exercices, les solutions et les
vérifications (encodées, jamais en clair) sont
livrés avec le paquet (dossier fhecli/data). Ils ne sont jamais modifiés :
l'étudiant travaille sur une copie, dans son espace de travail (`fhe-cli init`).
"""

from importlib.resources import files

from fhecli import solutions

DATA = files("fhecli") / "data"


def info_text() -> str:
    return (DATA / "info.toml").read_text(encoding="utf-8")


def original_text(name: str) -> str:
    return (DATA / "originals" / f"{name}.py").read_text(encoding="utf-8")


def has_solution(name: str) -> bool:
    return (DATA / "solutions" / f"{name}.sol").is_file()


def solution_text(name: str) -> str:
    return solutions.decode((DATA / "solutions" / f"{name}.sol").read_text(encoding="ascii"))


def has_check(name: str) -> bool:
    return (DATA / "checks" / f"{name}.chk").is_file()


def check_text(name: str) -> str:
    """Vérifications (tests pytest) d'un exercice, décodées en mémoire."""
    blob = (DATA / "checks" / f"{name}.chk").read_text(encoding="ascii")
    return solutions.decode(blob, solutions.CHECK_HEADER)
