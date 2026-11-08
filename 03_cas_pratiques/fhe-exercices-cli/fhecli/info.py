"""Chargement de la liste des exercices depuis info.toml."""

import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Exercise:
    name: str
    category: str
    title: str
    difficulty: str
    bonus: bool
    hint: str
    path: Path
    original_path: Path
    solution_path: Path


def load_exercises(root: Path = ROOT) -> list[Exercise]:
    data = tomllib.loads((root / "info.toml").read_text(encoding="utf-8"))
    exercises = []
    for item in data["exercises"]:
        name = item["name"]
        exercises.append(
            Exercise(
                name=name,
                category=item["category"],
                title=item["title"],
                difficulty=item.get("difficulty", ""),
                bonus=item.get("bonus", False),
                hint=item.get("hint", ""),
                path=root / "exercises" / f"{name}.py",
                original_path=root / "originals" / f"{name}.py",
                solution_path=root / "solutions" / f"{name}.py",
            )
        )
    return exercises


def find_exercise(root: Path, name: str) -> Exercise | None:
    for ex in load_exercises(root):
        if ex.name == name:
            return ex
    return None
