"""Point d'entrée de la commande `fhecli`."""

import argparse
import sys
from pathlib import Path

from fhecli import __version__, resources, ui
from fhecli.info import exercise_names, find_exercise, load_exercises
from fhecli.runner import PYTEST_SUBCOMMAND, has_marker, run_tests, status
from fhecli.watch import watch as watch_loop
from fhecli.workspace import DEFAULT_DIR, WorkspaceNotFound, find_workspace, init_workspace

# Codes de sortie
EXIT_OK = 0
EXIT_ERROR = 1          # tests en échec, exercice inconnu, pas d'espace de travail...
EXIT_MARKER_LEFT = 2    # tests OK mais « # I AM NOT DONE » encore présent

STATUS_ICON = {
    "done": ui.success("[x]"),
    "almost": ui.warn("[~]"),
    "pending": ui.failure("[ ]"),
}


def _workspace() -> Path:
    try:
        return find_workspace()
    except WorkspaceNotFound:
        print(ui.failure("Aucun espace de travail fhecli trouvé dans ce dossier ni dans ses parents."))
        print(f"Lancez d'abord {ui.bold('fhecli init')} (il crée le dossier ./{DEFAULT_DIR}),")
        print("puis placez-vous dans ce dossier.")
        raise SystemExit(EXIT_ERROR)


def _exercise_or_exit(name: str):
    ex = find_exercise(_workspace(), name)
    if ex is None:
        print(ui.failure(f"Exercice inconnu : {name}"))
        print(f"Utilisez {ui.bold('fhecli list')} pour voir les noms disponibles.")
        raise SystemExit(EXIT_ERROR)
    return ex


def cmd_init(args) -> int:
    target = Path(args.directory)
    try:
        ws = init_workspace(target, exercise_names())
    except FileExistsError:
        print(ui.failure(f"Un espace de travail existe déjà dans {target.resolve()}."))
        print("Rien n'a été modifié. Choisissez un autre dossier : fhecli init <dossier>")
        return EXIT_ERROR
    print(ui.success(f"Espace de travail créé : {ws}"))
    print()
    print("Pour commencer :")
    print(f"  cd {ws}")
    print("  fhecli watch")
    return EXIT_OK


def cmd_list(args) -> int:
    exercises = load_exercises(_workspace())
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
    print(f"Progression : {done_count}/{len(exercises)} exercices résolus.")
    print(ui.DIM + "[x] résolu   [~] tests OK, marqueur à retirer   [ ] pas encore bon" + ui.RESET)
    return EXIT_OK


def cmd_run(args) -> int:
    ex = _exercise_or_exit(args.name)
    print(ui.bold(f"{ex.name} - {ex.title}"))
    print(f"Fichier : {ex.path}")
    print()
    passed, output = run_tests(ex.path)
    print(output)
    print()
    if passed and has_marker(ex.path):
        print(ui.warn(
            "Tests OK, mais le fichier contient encore « # I AM NOT DONE ». "
            "Retirez cette ligne une fois satisfait de votre solution."
        ))
        return EXIT_MARKER_LEFT
    if passed:
        print(ui.success("Tous les tests passent."))
        return EXIT_OK
    print(ui.failure("Des tests échouent encore."))
    print(f"Besoin d'un coup de pouce ? {ui.bold('fhecli hint ' + ex.name)}")
    return EXIT_ERROR


def cmd_hint(args) -> int:
    ex = _exercise_or_exit(args.name)
    print(ui.bold(f"Indice pour {ex.name} :"))
    print(ex.hint or "Pas d'indice supplémentaire : relisez le docstring en haut du fichier.")
    return EXIT_OK


def cmd_solution(args) -> int:
    ex = _exercise_or_exit(args.name)
    if not resources.has_solution(ex.name):
        print(ui.failure("Pas de solution disponible pour cet exercice."))
        return EXIT_ERROR
    if status(ex.path) != "done":
        print(ui.warn(f"La solution de {ex.name} est verrouillée."))
        print("Elle se débloque quand l'exercice est résolu : les tests passent ET la")
        print("ligne « # I AM NOT DONE » a été retirée du fichier.")
        print(f"Vérifiez où vous en êtes avec {ui.bold('fhecli run ' + ex.name)}, "
              f"ou demandez un indice avec {ui.bold('fhecli hint ' + ex.name)}.")
        return EXIT_ERROR
    print(ui.bold(f"Solution de référence pour {ex.name} :"))
    print(ui.rule())
    print(resources.solution_text(ex.name))
    print(ui.rule())
    return EXIT_OK


def cmd_reset(args) -> int:
    ws = _workspace()
    if args.all:
        targets = load_exercises(ws)
        question = (f"Remettre les {len(targets)} exercices à leur énoncé de départ ? "
                    "Tout votre code sera perdu.")
    elif args.name:
        targets = [_exercise_or_exit(args.name)]
        question = f"Remettre {targets[0].name} à son énoncé de départ ? Votre code sera perdu."
    else:
        print(ui.failure("Précisez un nom d'exercice, ou utilisez --all."))
        return EXIT_ERROR

    if not args.yes and not ui.confirm(question):
        print("Annulé, rien n'a été modifié.")
        return EXIT_OK

    for ex in targets:
        ex.path.parent.mkdir(parents=True, exist_ok=True)
        ex.path.write_text(resources.original_text(ex.name), encoding="utf-8")
    if args.all:
        print(ui.success(f"Les {len(targets)} exercices ont été réinitialisés."))
    else:
        print(ui.success(f"{targets[0].name} a été réinitialisé à son énoncé de départ."))
    return EXIT_OK


def cmd_watch(args) -> int:
    watch_loop(load_exercises(_workspace()))
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fhecli",
        description=(
            "Atelier d'exercices en ligne de commande : chiffrement classique "
            "et chiffrement homomorphe (FHE). Inspiré de rustlings."
        ),
        epilog="Pour commencer : fhecli init, puis cd fhe-exercices et fhecli watch.",
    )
    parser.add_argument("--version", action="version", version=f"fhecli {__version__}")
    sub = parser.add_subparsers(dest="command", required=True, metavar="commande")

    p_init = sub.add_parser("init", help="Crée un espace de travail avec les exercices")
    p_init.add_argument("directory", nargs="?", default=DEFAULT_DIR,
                        help=f"Dossier à créer (défaut : {DEFAULT_DIR})")
    p_init.set_defaults(func=cmd_init)

    p_watch = sub.add_parser("watch", help="Mode guidé : avance exercice par exercice")
    p_watch.set_defaults(func=cmd_watch)

    p_list = sub.add_parser("list", help="Liste tous les exercices et leur statut")
    p_list.set_defaults(func=cmd_list)

    p_run = sub.add_parser("run", help="Lance les tests d'un seul exercice")
    p_run.add_argument("name", help="Nom de l'exercice (ex : ex1_cesar)")
    p_run.set_defaults(func=cmd_run)

    p_hint = sub.add_parser("hint", help="Affiche un indice pour un exercice")
    p_hint.add_argument("name")
    p_hint.set_defaults(func=cmd_hint)

    p_solution = sub.add_parser("solution", help="Affiche la solution (une fois l'exercice résolu)")
    p_solution.add_argument("name")
    p_solution.set_defaults(func=cmd_solution)

    p_reset = sub.add_parser("reset", help="Remet un exercice à son énoncé de départ")
    p_reset.add_argument("name", nargs="?", help="Nom de l'exercice (à omettre avec --all)")
    p_reset.add_argument("--all", action="store_true", help="Réinitialise tous les exercices")
    p_reset.add_argument("-y", "--yes", action="store_true", help="Ne pas demander de confirmation")
    p_reset.set_defaults(func=cmd_reset)

    return parser


def main(argv: list[str] | None = None) -> int:
    ui.setup_console()
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == PYTEST_SUBCOMMAND:
        # Usage interne (exécutable autonome) : `fhecli _run-pytest <args>`
        # exécute le pytest embarqué. Absent de l'aide.
        import pytest

        return int(pytest.main(argv[1:]))
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
