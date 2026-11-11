"""Mode « watch » : réexécute les vérifications de l'exercice courant à chaque
sauvegarde du fichier, et avance automatiquement une fois qu'il est résolu.
"""

import sys
import time

from fhecli import resources, ui
from fhecli.info import Exercise
from fhecli.runner import has_marker, run_tests

POLL_INTERVAL = 0.5


def _print_exercise_banner(ex: Exercise, index: int, total: int) -> None:
    print()
    print(ui.rule("="))
    print(ui.bold(f"Exercice {index}/{total} : {ex.name} - {ex.title}"))
    print(f"{ui.info(ex.category)}" + (f"  {ui.warn('[bonus]')}" if ex.bonus else ""))
    print(ui.rule("="))
    print(f"Fichier à éditer : {ex.path}")
    print(ui.DIM + "En attente de modifications... (Ctrl+C pour quitter)" + ui.RESET)


def _run_and_report(ex: Exercise) -> bool:
    passed, output = run_tests(ex.path)
    print()
    if passed:
        print(ui.success("Vérifications : OK"))
    else:
        print(ui.failure("Vérifications : ÉCHEC"))
        print(output)
    return passed


def _first_pending(exercises: list[Exercise]) -> Exercise | None:
    for ex in exercises:
        passed, _ = run_tests(ex.path)
        if not (passed and not has_marker(ex.path)):
            return ex
    return None


def _offer_solution(ex: Exercise) -> None:
    """Après une réussite, propose d'afficher la solution de référence
    (uniquement dans un vrai terminal interactif)."""
    # stdin ET stdout : sous Windows, le périphérique NUL se déclare « tty ».
    if not (sys.stdin.isatty() and sys.stdout.isatty() and resources.has_solution(ex.name)):
        return
    if ui.confirm("Exercice résolu ! Voir la solution de référence pour comparer ?"):
        print(ui.rule())
        print(resources.solution_text(ex.name))
        print(ui.rule())


def watch(exercises: list[Exercise]) -> None:
    total = len(exercises)
    print(ui.bold("fhe-cli start") + " - atelier guidé")
    print("Résolvez les exercices dans l'ordre. Dès que les vérifications d'un")
    print("exercice passent, retirez le commentaire « # I AM NOT DONE » en")
    print("haut du fichier : l'outil passera alors au suivant.")

    try:
        while True:
            current = _first_pending(exercises)
            if current is None:
                print()
                print(ui.rule("*"))
                print(ui.success(ui.bold("Félicitations, vous avez terminé tous les exercices !")))
                print(ui.rule("*"))
                return

            index = exercises.index(current) + 1
            _print_exercise_banner(current, index, total)
            # Date relevée AVANT de lancer les tests : une sauvegarde faite
            # pendant leur exécution sera bien détectée au prochain passage.
            last_mtime = _safe_mtime(current.path)
            passed = _run_and_report(current)
            if passed and not has_marker(current.path):
                # Résolu entre-temps (fichier sauvegardé pendant l'analyse) :
                # on avance sans attendre une nouvelle sauvegarde.
                print(ui.success("Exercice résolu, passage au suivant..."))
                _offer_solution(current)
                continue
            if passed:
                print(ui.warn(
                    "Vérifications OK ! Retirez « # I AM NOT DONE » en haut du fichier "
                    "pour passer au suivant."
                ))

            while True:
                time.sleep(POLL_INTERVAL)
                mtime = _safe_mtime(current.path)
                if mtime is not None and mtime != last_mtime:
                    last_mtime = mtime
                    time.sleep(0.15)  # laisse l'éditeur finir d'écrire le fichier
                    passed = _run_and_report(current)
                    if passed and not has_marker(current.path):
                        print(ui.success("Exercice résolu, passage au suivant..."))
                        _offer_solution(current)
                        break
                    if passed and has_marker(current.path):
                        print(ui.warn(
                            "Vérifications OK ! Retirez « # I AM NOT DONE » en haut du "
                            "fichier pour passer au suivant."
                        ))
    except KeyboardInterrupt:
        print()
        print(ui.info("À bientôt !"))


def _safe_mtime(path):
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return None
