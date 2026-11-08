"""Liste des exercices (info.toml embarqué dans le paquet)."""

import tomllib
from dataclasses import dataclass
from pathlib import Path

from fhecli import resources
from fhecli.workspace import EXERCISES_DIR


@dataclass
class Exercise:
    name: str
    category: str
    title: str
    difficulty: str
    bonus: bool
    hint: str
    path: Path  # fichier de l'étudiant, dans son espace de travail


def exercise_names() -> list[str]:
    return [item["name"] for item in tomllib.loads(resources.info_text())["exercises"]]


def load_exercises(workspace: Path) -> list[Exercise]:
    data = tomllib.loads(resources.info_text())
    return [
        Exercise(
            name=item["name"],
            category=item["category"],
            title=item["title"],
            difficulty=item.get("difficulty", ""),
            bonus=item.get("bonus", False),
            hint=item.get("hint", ""),
            path=workspace / EXERCISES_DIR / f"{item['name']}.py",
        )
        for item in data["exercises"]
    ]


def find_exercise(workspace: Path, name: str) -> Exercise | None:
    for ex in load_exercises(workspace):
        if ex.name == name:
            return ex
    return None
