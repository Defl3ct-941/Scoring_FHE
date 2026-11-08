import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app import grader, progress_store

WORKSPACE_DIR = Path("/app/workspace")
SOLUTIONS_DIR = Path("/app/solutions")
STUBS_DIR = Path("/app/stubs")
STATIC_DIR = "app/static"

app = FastAPI(title="Exercices FHE : Runner")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def discover_exercises() -> dict:
    """Scanne WORKSPACE_DIR et renvoie {id: {meta, dir}} trie par 'order'."""
    exercises = {}
    for child in sorted(WORKSPACE_DIR.iterdir()):
        meta_path = child / "meta.json"
        if child.is_dir() and meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            exercises[meta["id"]] = {"meta": meta, "dir": child}
    return dict(sorted(exercises.items(), key=lambda kv: kv[1]["meta"].get("order", 999)))


def get_exercise_or_404(exercise_id: str) -> dict:
    exercises = discover_exercises()
    if exercise_id not in exercises:
        raise HTTPException(status_code=404, detail="Exercice inconnu")
    return exercises[exercise_id]


def is_locked(meta: dict, progress: dict) -> tuple[bool, list[str]]:
    missing = [
        dep for dep in meta.get("depends_on", [])
        if not progress.get(dep, {}).get("passed", False)
    ]
    return (len(missing) > 0, missing)


class SaveBody(BaseModel):
    code: str


@app.get("/")
def index():
    return FileResponse(f"{STATIC_DIR}/index.html")


@app.get("/api/exercises")
def list_exercises():
    exercises = discover_exercises()
    progress = progress_store.get_all()
    result = []
    for ex_id, entry in exercises.items():
        meta = entry["meta"]
        locked, missing = is_locked(meta, progress)
        p = progress.get(ex_id, {"passed": False, "attempts": 0, "last_run": None})
        result.append({
            **meta,
            "locked": locked,
            "missing_dependencies": missing,
            "passed": p.get("passed", False),
            "attempts": p.get("attempts", 0),
            "last_result": p.get("last_result"),
        })
    return {"exercises": result}


@app.get("/api/exercises/{exercise_id}")
def get_exercise(exercise_id: str):
    entry = get_exercise_or_404(exercise_id)
    meta, ex_dir = entry["meta"], entry["dir"]
    progress = progress_store.get_all()
    locked, missing = is_locked(meta, progress)

    return {
        **meta,
        "locked": locked,
        "missing_dependencies": missing,
        "statement": (ex_dir / "README.md").read_text(encoding="utf-8"),
        "code": (ex_dir / "exercise.py").read_text(encoding="utf-8"),
        "test_code": (ex_dir / "test_exercise.py").read_text(encoding="utf-8"),
        "progress": progress.get(exercise_id, {"passed": False, "attempts": 0}),
    }


@app.post("/api/exercises/{exercise_id}/save")
def save_exercise(exercise_id: str, body: SaveBody):
    entry = get_exercise_or_404(exercise_id)
    meta, ex_dir = entry["meta"], entry["dir"]
    progress = progress_store.get_all()
    locked, missing = is_locked(meta, progress)
    if locked:
        raise HTTPException(status_code=423, detail=f"Exercice verrouille (termine d'abord : {missing})")

    (ex_dir / "exercise.py").write_text(body.code, encoding="utf-8")
    return {"ok": True}


@app.post("/api/exercises/{exercise_id}/run")
def run_exercise(exercise_id: str):
    entry = get_exercise_or_404(exercise_id)
    meta, ex_dir = entry["meta"], entry["dir"]
    progress = progress_store.get_all()
    locked, missing = is_locked(meta, progress)
    if locked:
        raise HTTPException(status_code=423, detail=f"Exercice verrouille (termine d'abord : {missing})")

    result = grader.run_tests(ex_dir)
    progress_store.record_run(exercise_id, result["passed"])
    return result


def _restore_stub(exercise_id: str, ex_dir: Path) -> None:
    stub_path = STUBS_DIR / exercise_id / "exercise.py"
    if not stub_path.exists():
        raise HTTPException(status_code=500, detail=f"Stub introuvable pour {exercise_id}")
    (ex_dir / "exercise.py").write_text(stub_path.read_text(encoding="utf-8"), encoding="utf-8")


@app.post("/api/exercises/{exercise_id}/reset")
def reset_exercise(exercise_id: str):
    """Remet exercise.py dans son etat de depart et efface la progression de CET exercice."""
    entry = get_exercise_or_404(exercise_id)
    ex_dir = entry["dir"]

    _restore_stub(exercise_id, ex_dir)
    progress_store.reset_one(exercise_id)

    return {"ok": True, "code": (ex_dir / "exercise.py").read_text(encoding="utf-8")}


@app.post("/api/reset-all")
def reset_all_exercises():
    """Remet TOUS les exercices dans leur etat de depart et efface toute la progression."""
    exercises = discover_exercises()
    for exercise_id, entry in exercises.items():
        _restore_stub(exercise_id, entry["dir"])
    progress_store.reset_all()
    return {"ok": True, "reset_count": len(exercises)}


@app.get("/api/exercises/{exercise_id}/solution")
def get_solution(exercise_id: str):
    entry = get_exercise_or_404(exercise_id)
    solution_path = SOLUTIONS_DIR / exercise_id / "solution.py"
    if not solution_path.exists():
        raise HTTPException(status_code=404, detail="Pas de solution disponible")
    return {"solution": solution_path.read_text(encoding="utf-8")}


@app.get("/api/progress")
def get_progress():
    exercises = discover_exercises()
    progress = progress_store.get_all()
    total = len(exercises)
    passed = sum(1 for ex_id in exercises if progress.get(ex_id, {}).get("passed", False))
    return {"total": total, "passed": passed, "progress": progress}
