"""Petits helpers de sortie terminal (couleurs ANSI, sans dependance externe)."""

import os
import sys

if os.name == "nt":
    # Active l'interpretation des sequences ANSI dans les vieilles consoles
    # Windows (cmd.exe). Sans effet et sans danger sur les terminaux modernes
    # (Windows Terminal, VS Code) qui la supportent deja nativement.
    os.system("")

_ENABLED = sys.stdout.isatty()

RESET = "\033[0m" if _ENABLED else ""
BOLD = "\033[1m" if _ENABLED else ""
DIM = "\033[2m" if _ENABLED else ""
GREEN = "\033[32m" if _ENABLED else ""
RED = "\033[31m" if _ENABLED else ""
YELLOW = "\033[33m" if _ENABLED else ""
CYAN = "\033[36m" if _ENABLED else ""
MAGENTA = "\033[35m" if _ENABLED else ""


def color(text: str, code: str) -> str:
    return f"{code}{text}{RESET}"


def success(text: str) -> str:
    return color(text, GREEN)


def failure(text: str) -> str:
    return color(text, RED)


def warn(text: str) -> str:
    return color(text, YELLOW)


def info(text: str) -> str:
    return color(text, CYAN)


def bold(text: str) -> str:
    return color(text, BOLD)


def rule(char: str = "-", width: int = 70) -> str:
    return char * width
