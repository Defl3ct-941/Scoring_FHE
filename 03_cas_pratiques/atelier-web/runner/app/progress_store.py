"""Persistance tres simple de la progression (un fichier JSON)."""

import json
import threading
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path("/app/data")
PROGRESS_FILE = DATA_DIR / "progress.json"

_lock = threading.Lock()


def _read() -> dict:
    if not PROGRESS_FILE.exists():
        return {}
    try:
        return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _write(data: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROGRESS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def get_all() -> dict:
    with _lock:
        return _read()


def get(exercise_id: str) -> dict:
    with _lock:
        return _read().get(exercise_id, {"passed": False, "attempts": 0, "last_run": None})


def record_run(exercise_id: str, passed: bool) -> dict:
    with _lock:
        data = _read()
        entry = data.get(exercise_id, {"passed": False, "attempts": 0, "last_run": None})
        entry["attempts"] = entry.get("attempts", 0) + 1
        entry["passed"] = entry.get("passed", False) or passed
        entry["last_run"] = datetime.now(timezone.utc).isoformat()
        entry["last_result"] = passed
        data[exercise_id] = entry
        _write(data)
        return entry


def reset_one(exercise_id: str) -> None:
    """Efface la progression d'un seul exercice (remet a zero passed/attempts)."""
    with _lock:
        data = _read()
        data.pop(exercise_id, None)
        _write(data)


def reset_all() -> None:
    """Efface toute la progression."""
    with _lock:
        _write({})
