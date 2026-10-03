import json
from pathlib import Path

STATE_FILE = Path(__file__).parent / "state.json"

def create_empty_state():
    return {
        "status": "idle",
        "pending_task": None
    }

def load_state():
    if not STATE_FILE.exists():
        return create_empty_state()

    with STATE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)

def save_state(state):
    with STATE_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            state,
            file,
            ensure_ascii=False,
            indent=2
        )