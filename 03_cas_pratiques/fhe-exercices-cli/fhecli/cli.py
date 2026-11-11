"""Point d'entrée de la commande `fhe-cli` (alias historique : `fhecli`)."""

import argparse
import re
import sys
from pathlib import Path

from fhecli import __version__, resources, ui
from fhecli.info import exercise_names, find_exercise, load_exercises
from fhecli.runner import PYTEST_SUBCOMMAND, check_exercise, has_marker, run_tests, status
from fhecli.watch import watch as watch_loop
from fhecli.workspace import DEFAULT_DIR, WorkspaceNotFound, find_workspace, init_workspace

PROG = "fhe-cli"

# Codes de sortie
EXIT_OK = 0
EXIT_ERROR = 1          # tests en échec, exercice inconnu, pas d'espace de travail...
EXIT_MARKER_LEFT = 2    # tests OK mais « # I AM NOT DONE » encore présent
EXIT_USAGE = 2          # commande ou arguments invalides

STATUS_ICON = {
    "done": ui.success("[x]"),
    "almost": ui.warn("[~]"),
    "pending": ui.failure("[ ]"),
}

# Aide de chaque commande : (syntaxe, résumé en une ligne, explication détaillée).
COMMANDS = {
    "init": (
        "init [dossier]",
        "Crée votre espace de travail avec tous les exercices",
        f"Crée le dossier indiqué (par défaut : ./{DEFAULT_DIR}) et y copie les énoncés\n"
        "des exercices. Refuse d'écraser un espace de travail existant.\n"
        f"Exemple : {PROG} init   puis   cd {DEFAULT_DIR}",
    ),
    "start": (
        "start",
        "Lance l'atelier guidé, exercice par exercice",
        "Affiche l'exercice en cours, relance ses tests à chaque sauvegarde du\n"
        "fichier et passe au suivant dès qu'il est résolu (tests OK et ligne\n"
        "« # I AM NOT DONE » retirée). Ctrl+C pour quitter.",
    ),
    "next": (
        "next",
        "Passe au prochain exercice à résoudre et le teste",
        "Choisit automatiquement le premier exercice pas encore résolu (dans\n"
        "l'ordre de la liste), affiche son nom et son fichier, puis lance ses tests.\n"
        "Si tout est résolu, affiche un message de félicitations.",
    ),
    "previous": (
        "previous",
        "Revient à l'exercice précédent et le teste",
        "Choisit l'exercice qui précède le prochain à résoudre, affiche son nom et\n"
        "son fichier, puis lance ses tests. Utile pour revoir ce que vous venez de faire.",
    ),
    "list": (
        "list",
        "Affiche tous les exercices et votre progression",
        "Liste les exercices par catégorie avec leur état : [x] résolu,\n"
        "[~] tests OK mais ligne « # I AM NOT DONE » à retirer, [ ] pas encore bon.",
    ),
    "check": (
        "check [exercice | --all]",
        "Vérifie si un exercice est résolu",
        "Lance les vérifications de l'exercice (cachées : elles ne sont pas dans\n"
        "votre fichier) et affiche, pour chacune, si elle passe ou non.\n"
        "Sans argument : vérifie le prochain exercice à résoudre.\n"
        "  --all     vérifie tous les exercices et affiche le bilan\n"
        "Codes de sortie : 0 résolu, 1 vérifications en échec, 2 vérifications OK\n"
        "mais ligne « # I AM NOT DONE » encore présente.\n"
        f"Exemples : {PROG} check ex1    {PROG} check --all",
    ),
    "run": (
        "run <exercice>",
        "Teste un exercice et affiche le résultat",
        "Lance les tests d'un seul exercice. Codes de sortie : 0 résolu, 1 tests en\n"
        "échec, 2 tests OK mais ligne « # I AM NOT DONE » encore présente.\n"
        f"Exemple : {PROG} run ex1",
    ),
    "hint": (
        "hint <exercice>",
        "Affiche un indice pour un exercice",
        f"Exemple : {PROG} hint ex1",
    ),
    "solution": (
        "solution <exercice>",
        "Affiche la solution (une fois l'exercice résolu)",
        "La solution de référence est verrouillée tant que l'exercice n'est pas\n"
        "résolu (tests OK et ligne « # I AM NOT DONE » retirée).",
    ),
    "reset": (
        "reset <exercice> | --all [-y]",
        "Remet un exercice (ou tous) à l'énoncé de départ",
        "Demande confirmation avant d'effacer votre code.\n"
        "  --all     réinitialise tous les exercices\n"
        "  -y        ne pas demander de confirmation\n"
        f"Exemples : {PROG} reset ex1    {PROG} reset --all",
    ),
    "help": (
        "help [commande]",
        "Affiche cette aide, ou le détail d'une commande",
        f"Exemple : {PROG} help run",
    ),
}
ALIASES = {"watch": "start"}  # ancien nom, toujours accepté


def general_help() -> str:
    width = max(len(syntax) for syntax, _, _ in COMMANDS.values()) + 2
    lines = [
        ui.bold(f"{PROG} {__version__}") + " : atelier d'exercices de chiffrement classique et homomorphe (FHE)",
        "",
        f"Utilisation : {PROG} <commande> [arguments]",
        "",
        ui.bold("Pour commencer :"),
        f"  {PROG} init          crée le dossier {DEFAULT_DIR} avec les exercices",
        f"  cd {DEFAULT_DIR}",
        f"  {PROG} start         lance l'atelier guidé",
        "",
        ui.bold("Commandes :"),
    ]
    lines += [f"  {syntax:<{width}}{summary}" for syntax, summary, _ in COMMANDS.values()]
    lines += [
        "",
        ui.bold("Options :"),
        f"  {'-h, --help':<{width}}Affiche cette aide",
        f"  {'--version':<{width}}Affiche la version",
        "",
        f"Détail d'une commande : {PROG} help <commande>   (ou {PROG} <commande> --help)",
        "",
        "Un exercice se désigne par son nom complet (ex1_cesar) ou son alias :",
        "ex1, exo1 ou simplement 1.",
        "",
        ui.DIM + f"Alias disponibles : fhecli (ancien nom de {PROG}), {PROG} watch (= {PROG} start)." + ui.RESET,
    ]
    return "\n".join(lines)


def command_help(name: str) -> str:
    syntax, summary, details = COMMANDS[name]
    return "\n".join([ui.bold(f"{PROG} {syntax}"), "", summary + ".", "", details])


class _HelpAction(argparse.Action):
    """-h / --help : affiche notre aide en français au lieu de celle d'argparse."""

    def __init__(self, option_strings, dest, command=None, **kwargs):
        super().__init__(option_strings, dest, nargs=0, default=argparse.SUPPRESS, **kwargs)
        self.command = command

    def __call__(self, parser, namespace, values, option_string=None):
        print(command_help(self.command) if self.command else general_help())
        parser.exit(EXIT_OK)


class _Parser(argparse.ArgumentParser):
    """Messages d'erreur en français, avec un renvoi vers l'aide."""

    def error(self, message):
        unknown = re.search(r"invalid choice: '([^']*)'", message)
        if unknown:
            message = f"commande inconnue : {unknown.group(1)}"
        else:
            message = (message.replace("the following arguments are required:", "argument manquant :")
                              .replace("unrecognized arguments:", "arguments non reconnus :"))
        print(ui.failure(f"Erreur : {message}"), file=sys.stderr)
        print(f"Tapez {ui.bold(PROG + ' help')} pour la liste des commandes.", file=sys.stderr)
        self.exit(EXIT_USAGE)


def _workspace() -> Path:
    try:
        return find_workspace()
    except WorkspaceNotFound:
        print(ui.failure("Aucun espace de travail trouvé dans ce dossier ni dans ses parents."))
        print(f"Lancez d'abord {ui.bold(PROG + ' init')} (il crée le dossier ./{DEFAULT_DIR}),")
        print("puis placez-vous dans ce dossier.")
        raise SystemExit(EXIT_ERROR)


def _exercise_or_exit(name: str):
    ex = find_exercise(_workspace(), name)
    if ex is None:
        print(ui.failure(f"Exercice inconnu : {name}"))
        print(f"Utilisez {ui.bold(PROG + ' list')} pour voir les noms disponibles.")
        raise SystemExit(EXIT_ERROR)
    return ex


def cmd_init(args) -> int:
    target = Path(args.directory)
    try:
        ws = init_workspace(target, exercise_names())
    except FileExistsError:
        print(ui.failure(f"Un espace de travail existe déjà dans {target.resolve()}."))
        print(f"Rien n'a été modifié. Choisissez un autre dossier : {PROG} init <dossier>")
        return EXIT_ERROR
    print(ui.success(f"Espace de travail créé : {ws}"))
    print()
    print("Pour commencer :")
    print(f"  cd {ws}")
    print(f"  {PROG} start")
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
        print(f"  {STATUS_ICON[st]} {ex.alias:<5} {ex.name:<24} {ex.title}{bonus_tag}")
    print()
    print(f"Progression : {done_count}/{len(exercises)} exercices résolus.")
    print(ui.DIM + "[x] résolu   [~] tests OK, marqueur à retirer   [ ] pas encore bon" + ui.RESET)
    return EXIT_OK


def cmd_run(args) -> int:
    return _run_exercise(_exercise_or_exit(args.name))


def _run_exercise(ex) -> int:
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
    print(f"Besoin d'un coup de pouce ? {ui.bold(PROG + ' hint ' + ex.alias)}")
    return EXIT_ERROR


CHECK_ICON = {"PASSED": ui.success("[ok]"), "SKIPPED": ui.warn("[--]"), "XFAIL": ui.success("[ok]")}


def _readable(test_name: str) -> str:
    return test_name.removeprefix("test_").replace("_", " ")


def _check_one(ex, verbose: bool = True) -> int:
    report = check_exercise(ex.path)
    marker = has_marker(ex.path)
    if report.passed and not marker:
        code, verdict = EXIT_OK, ui.success("résolu")
    elif report.passed:
        code, verdict = EXIT_MARKER_LEFT, ui.warn("vérifications OK, ligne « # I AM NOT DONE » à retirer")
    else:
        code, verdict = EXIT_ERROR, ui.failure("pas encore résolu")
    ok = sum(1 for _, outcome in report.results if outcome in {"PASSED", "XFAIL", "SKIPPED"})
    total = len(report.results)
    if not verbose:
        score = f"{ok}/{total}" if total else "-"
        print(f"  {STATUS_ICON[{EXIT_OK: 'done', EXIT_MARKER_LEFT: 'almost'}.get(code, 'pending')]} "
              f"{ex.alias:<5} {ex.name:<24} {score:>5}  {verdict}")
        return code
    print(ui.bold(f"Vérification de {ex.name} ({ex.alias}) - {ex.title}"))
    print(f"Fichier : {ex.path}")
    print()
    for test, outcome in report.results:
        icon = CHECK_ICON.get(outcome, ui.failure("[xx]"))
        print(f"  {icon} {_readable(test)}" + (ui.DIM + " (ignorée)" + ui.RESET if outcome == "SKIPPED" else ""))
    if not report.results:
        print(report.output)  # erreur avant toute vérification (syntaxe, import...)
    elif not report.passed:
        errors = list(dict.fromkeys(  # sans doublons, dans l'ordre
            line.strip() for line in report.output.splitlines()
            if line.startswith("E ") or (line.startswith(str(ex.path)) and re.search(r":\d+: ", line))))
        if errors:
            print()
            print(ui.DIM + "Détail des échecs :" + ui.RESET)
            for line in errors[:12]:
                print("  " + line)
    print()
    if not report.results:
        print(ui.failure("Aucune vérification n'a pu être lancée : corrigez l'erreur ci-dessus."))
        return EXIT_ERROR
    print(f"{ok}/{total} vérifications réussies : {verdict}.")
    if code == EXIT_MARKER_LEFT:
        print("Retirez la ligne « # I AM NOT DONE » du fichier pour valider l'exercice.")
    elif code == EXIT_ERROR:
        print(f"Besoin d'un coup de pouce ? {ui.bold(PROG + ' hint ' + ex.alias)}")
    else:
        print(f"Comparez avec la solution de référence : {ui.bold(PROG + ' solution ' + ex.alias)}")
    return code


def cmd_check(args) -> int:
    if args.all:
        exercises = load_exercises(_workspace())
        print(ui.bold(f"Vérification des {len(exercises)} exercices :"))
        codes = [_check_one(ex, verbose=False) for ex in exercises]
        done = codes.count(EXIT_OK)
        print()
        print(f"Progression : {done}/{len(exercises)} exercices résolus.")
        return EXIT_OK if done == len(exercises) else EXIT_ERROR
    if args.name:
        return _check_one(_exercise_or_exit(args.name))
    exercises = load_exercises(_workspace())
    index = _first_pending_index(exercises)
    if index is None:
        print(ui.success(ui.bold("Tous les exercices sont résolus, bravo !")))
        return EXIT_OK
    return _check_one(exercises[index])


def _first_pending_index(exercises) -> int | None:
    """Index du premier exercice pas encore résolu (None si tout est résolu)."""
    for index, ex in enumerate(exercises):
        if status(ex.path) != "done":
            return index
    return None


def cmd_next(args) -> int:
    exercises = load_exercises(_workspace())
    index = _first_pending_index(exercises)
    if index is None:
        print(ui.success(ui.bold("Félicitations, vous avez terminé tous les exercices !")))
        return EXIT_OK
    print(ui.info(f"Prochain exercice à résoudre ({index + 1}/{len(exercises)}) :"))
    return _run_exercise(exercises[index])


def cmd_previous(args) -> int:
    exercises = load_exercises(_workspace())
    index = _first_pending_index(exercises)
    if index is None:
        index = len(exercises)  # tout est résolu : le précédent est le dernier
    if index == 0:
        print("Pas d'exercice précédent.")
        return EXIT_OK
    print(ui.info(f"Exercice précédent ({index}/{len(exercises)}) :"))
    return _run_exercise(exercises[index - 1])


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
        print(f"Vérifiez où vous en êtes avec {ui.bold(PROG + ' check ' + ex.alias)}, "
              f"ou demandez un indice avec {ui.bold(PROG + ' hint ' + ex.alias)}.")
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
        print(f"Exemples : {PROG} reset ex1    {PROG} reset --all")
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


def cmd_start(args) -> int:
    watch_loop(load_exercises(_workspace()))
    return EXIT_OK


def cmd_help(args) -> int:
    if args.topic is None:
        print(general_help())
        return EXIT_OK
    topic = ALIASES.get(args.topic, args.topic)
    if topic not in COMMANDS:
        print(ui.failure(f"Commande inconnue : {args.topic}"))
        print(f"Tapez {ui.bold(PROG + ' help')} pour la liste des commandes.")
        return EXIT_USAGE
    print(command_help(topic))
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(prog=PROG, add_help=False)
    parser.add_argument("-h", "--help", action=_HelpAction)
    parser.add_argument("--version", action="version", version=f"{PROG} {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="commande", parser_class=_Parser)
    sub.required = True

    def add(name, func, aliases=()):
        p = sub.add_parser(name, aliases=list(aliases), add_help=False)
        p.add_argument("-h", "--help", action=_HelpAction, command=name)
        p.set_defaults(func=func)
        return p

    add("init", cmd_init).add_argument("directory", nargs="?", default=DEFAULT_DIR)
    add("start", cmd_start, aliases=ALIASES_FOR["start"])
    add("next", cmd_next)
    add("previous", cmd_previous)
    add("list", cmd_list)
    p_check = add("check", cmd_check)
    p_check.add_argument("name", nargs="?", metavar="exercice")
    p_check.add_argument("--all", action="store_true")
    add("run", cmd_run).add_argument("name", metavar="exercice")
    add("hint", cmd_hint).add_argument("name", metavar="exercice")
    add("solution", cmd_solution).add_argument("name", metavar="exercice")
    p_reset = add("reset", cmd_reset)
    p_reset.add_argument("name", nargs="?", metavar="exercice")
    p_reset.add_argument("--all", action="store_true")
    p_reset.add_argument("-y", "--yes", action="store_true")
    add("help", cmd_help).add_argument("topic", nargs="?")
    return parser


ALIASES_FOR = {"start": [alias for alias, target in ALIASES.items() if target == "start"]}


def main(argv: list[str] | None = None) -> int:
    ui.setup_console()
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == PYTEST_SUBCOMMAND:
        # Usage interne (exécutable autonome) : `fhe-cli _run-pytest <args>`
        # exécute le pytest embarqué. Absent de l'aide.
        import pytest

        return int(pytest.main(argv[1:]))
    if not argv:
        print(general_help())
        return EXIT_OK
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
