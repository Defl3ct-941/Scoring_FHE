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

    @property
    def number(self) -> str:
        """Numéro de l'exercice : « 1 » pour ex1_cesar."""
        return self.name.split("_", 1)[0].removeprefix("ex")

    @property
    def alias(self) -> str:
        """Nom court accepté partout à la place du nom complet : « ex1 »."""
        return f"ex{self.number}"

    def matches(self, name: str) -> bool:
        """Accepte le nom complet (ex1_cesar), l'alias (ex1), exo1 ou le numéro (1)."""
        name = name.strip().lower().removesuffix(".py")
        return name in {self.name, self.alias, f"exo{self.number}", self.number}


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
        if ex.matches(name):
            return ex
    return None
