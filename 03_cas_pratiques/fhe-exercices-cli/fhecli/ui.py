"""Petits utilitaires de terminal : couleurs ANSI, UTF-8, confirmations."""

import os
import sys

if os.name == "nt":
    # Active l'interprétation des séquences ANSI dans les vieilles consoles
    # Windows (cmd.exe). Sans effet sur les terminaux modernes.
    os.system("")

_ENABLED = sys.stdout.isatty() and "NO_COLOR" not in os.environ

RESET = "\033[0m" if _ENABLED else ""
BOLD = "\033[1m" if _ENABLED else ""
DIM = "\033[2m" if _ENABLED else ""
GREEN = "\033[32m" if _ENABLED else ""
RED = "\033[31m" if _ENABLED else ""
YELLOW = "\033[33m" if _ENABLED else ""
CYAN = "\033[36m" if _ENABLED else ""


def setup_console() -> None:
    """Force UTF-8 sur stdout/stderr (accents corrects dans les vieilles
    consoles Windows ou quand la sortie est redirigée)."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


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


YES_ANSWERS = ("o", "oui", "y", "yes")


def confirm(question: str) -> bool:
    """Pose une question oui/non. Entrée vide, EOF ou Ctrl+C valent « non »."""
    try:
        answer = input(f"{question} [o/N] ")
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return answer.strip().lower() in YES_ANSWERS
