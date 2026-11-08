"""Point d'entree de la commande `fhecli`."""

import argparse
import shutil
import sys

from fhecli import ui
from fhecli.info import ROOT, find_exercise, load_exercises
from fhecli.runner import has_marker, run_tests, status
from fhecli.watch import watch as watch_loop

STATUS_ICON = {
    "done": ui.success("[x]"),
    "almost": ui.warn("[~]"),
    "pending": ui.failure("[ ]"),
}


def cmd_list(args) -> int:
    exercises = load_exercises(ROOT)
    print(ui.bold(f"{len(exercises)} exercices :"))
    print()
    last_category = None
    done_count = 0
    for ex in exercises:
        if ex.category != last_category:
            print(ui.info(ex.category))
            last_category = ex.category
        st = status(ex.path)
        if st == "done":
            done_count += 1
        bonus_tag = ui.warn(" (bonus)") if ex.bonus else ""
        print(f"  {STATUS_ICON[st]} {ex.name:<24} {ex.title}{bonus_tag}")
    print()
    print(f"Progression : {done_count}/{len(exercises)} exercices resolus.")
    print(ui.DIM + "[x] resolu   [~] tests OK, marqueur a retirer   [ ] pas encore bon" + ui.RESET)
    return 0


def cmd_run(args) -> int:
    ex = find_exercise(ROOT, args.name)
    if ex is None:
        print(ui.failure(f"Exercice inconnu : {args.name}"))
        print("Utilisez 'fhecli list' pour voir les noms disponibles.")
        return 1

    print(ui.bold(f"{ex.name} - {ex.title}"))
    print(f"Fichier : {ex.path}")
    print()
    passed, output = run_tests(ex.path)
    print(output)
    print()
    if passed and has_marker(ex.path):
        print(ui.warn(
            "Tests OK, mais le fichier contient encore '# I AM NOT DONE'. "
            "Retirez cette ligne une fois que vous etes satisfait de votre solution."
        ))
        return 0
    if passed:
        print(ui.success("Tous les tests passent."))
        return 0

    print(ui.failure("Des tests echouent encore."))
    print(f"Besoin d'un coup de pouce ? {ui.bold('fhecli hint ' + ex.name)}")
    return 1


def cmd_hint(args) -> int:
    ex = find_exercise(ROOT, args.name)
    if ex is None:
        print(ui.failure(f"Exercice inconnu : {args.name}"))
        return 1
    print(ui.bold(f"Indice pour {ex.name} :"))
    print(ex.hint or "Pas d'indice supplementaire : relisez le docstring en haut du fichier.")
    return 0


def cmd_solution(args) -> int:
    ex = find_exercise(ROOT, args.name)
    if ex is None:
        print(ui.failure(f"Exercice inconnu : {args.name}"))
        return 1
    if not ex.solution_path.exists():
        print(ui.failure("Pas de solution disponible pour cet exercice."))
        return 1
    if not args.yes:
        answer = input(
            "Essayez vraiment de resoudre l'exercice par vous-meme d'abord. "
            "Afficher la solution ? [y/N] "
        )
        if answer.strip().lower() not in ("y", "yes", "o", "oui"):
            print("Annule.")
            return 0
    print(ui.rule())
    print(ex.solution_path.read_text(encoding="utf-8"))
    print(ui.rule())
    return 0


def cmd_reset(args) -> int:
    exercises = load_exercises(ROOT)
    if args.all:
        for ex in exercises:
            _reset_one(ex)
        print(ui.success(f"Les {len(exercises)} exercices ont ete reinitialises."))
        return 0

    if not args.name:
        print(ui.failure("Precisez un nom d'exercice, ou utilisez --all."))
        return 1

    ex = find_exercise(ROOT, args.name)
    if ex is None:
        print(ui.failure(f"Exercice inconnu : {args.name}"))
        return 1
    _reset_one(ex)
    print(ui.success(f"{ex.name} a ete reinitialise a son enonce de depart."))
    return 0


def _reset_one(ex) -> None:
    shutil.copyfile(ex.original_path, ex.path)


def cmd_watch(args) -> int:
    exercises = load_exercises(ROOT)
    watch_loop(exercises)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fhecli",
        description=(
            "Atelier d'exercices en ligne de commande : chiffrement classique "
            "et chiffrement homomorphe (FHE). Inspire de rustlings."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_watch = sub.add_parser("watch", help="Mode guide : avance exercice par exercice")
    p_watch.set_defaults(func=cmd_watch)

    p_list = sub.add_parser("list", help="Liste tous les exercices et leur statut")
    p_list.set_defaults(func=cmd_list)

    p_run = sub.add_parser("run", help="Lance les tests d'un seul exercice")
    p_run.add_argument("name", help="Nom de l'exercice (ex: ex1_cesar)")
    p_run.set_defaults(func=cmd_run)

    p_hint = sub.add_parser("hint", help="Affiche un indice pour un exercice")
    p_hint.add_argument("name")
    p_hint.set_defaults(func=cmd_hint)

    p_solution = sub.add_parser("solution", help="Affiche la solution de reference")
    p_solution.add_argument("name")
    p_solution.add_argument("-y", "--yes", action="store_true", help="Ne pas demander de confirmation")
    p_solution.set_defaults(func=cmd_solution)

    p_reset = sub.add_parser("reset", help="Restaure un exercice a son enonce de depart")
    p_reset.add_argument("name", nargs="?", help="Nom de l'exercice (omettre avec --all)")
    p_reset.add_argument("--all", action="store_true", help="Reinitialise tous les exercices")
    p_reset.set_defaults(func=cmd_reset)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
