"""Mode 'watch' : reexecute les tests de l'exercice courant a chaque
sauvegarde du fichier, et avance automatiquement une fois qu'il est resolu.
"""

import time

from fhecli import ui
from fhecli.info import Exercise
from fhecli.runner import has_marker, run_tests

POLL_INTERVAL = 0.5


def _print_exercise_banner(ex: Exercise, index: int, total: int) -> None:
    print()
    print(ui.rule("="))
    print(ui.bold(f"Exercice {index}/{total} : {ex.name} - {ex.title}"))
    print(f"{ui.info(ex.category)}" + (f"  {ui.warn('[bonus]')}" if ex.bonus else ""))
    print(ui.rule("="))
    print(f"Fichier a editer : {ex.path}")
    print(ui.DIM + "En attente de modifications... (Ctrl+C pour quitter)" + ui.RESET)


def _run_and_report(ex: Exercise) -> bool:
    passed, output = run_tests(ex.path)
    print()
    if passed:
        print(ui.success("Tests : OK"))
    else:
        print(ui.failure("Tests : ECHEC"))
        print(output)
    return passed


def _first_pending(exercises: list[Exercise]) -> Exercise | None:
    for ex in exercises:
        passed, _ = run_tests(ex.path)
        if not (passed and not has_marker(ex.path)):
            return ex
    return None


def watch(exercises: list[Exercise]) -> None:
    total = len(exercises)
    print(ui.bold("fhecli watch") + " - mode surveillance")
    print("Resolvez les exercices dans l'ordre. Des que les tests d'un")
    print("exercice passent, retirez le commentaire '# I AM NOT DONE' en")
    print("haut du fichier : l'outil passera alors au suivant.")

    try:
        while True:
            current = _first_pending(exercises)
            if current is None:
                print()
                print(ui.rule("*"))
                print(ui.success(ui.bold("Felicitations, vous avez termine tous les exercices !")))
                print(ui.rule("*"))
                return

            index = exercises.index(current) + 1
            _print_exercise_banner(current, index, total)
            passed = _run_and_report(current)
            if passed and has_marker(current.path):
                print(ui.warn(
                    "Tests OK ! Retirez '# I AM NOT DONE' en haut du fichier "
                    "pour passer au suivant."
                ))

            last_mtime = _safe_mtime(current.path)
            while True:
                time.sleep(POLL_INTERVAL)
                mtime = _safe_mtime(current.path)
                if mtime is not None and mtime != last_mtime:
                    last_mtime = mtime
                    time.sleep(0.15)  # laisse l'editeur finir d'ecrire le fichier
                    passed = _run_and_report(current)
                    if passed and not has_marker(current.path):
                        print(ui.success("Exercice resolu, passage au suivant..."))
                        break
                    if passed and has_marker(current.path):
                        print(ui.warn(
                            "Tests OK ! Retirez '# I AM NOT DONE' en haut du "
                            "fichier pour passer au suivant."
                        ))
    except KeyboardInterrupt:
        print()
        print(ui.info("A bientot !"))


def _safe_mtime(path):
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return None
