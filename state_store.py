import json
import re
from pathlib import Path

STATE_DIRECTORY = Path(__file__).parent / "states"

def create_empty_state():
    return {
        "status": "idle",
        "pending_task": None
    }

def get_state_path(conversation_id):
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", conversation_id):
        raise ValueError(
            "Sohbet kimliği 1-64 karakter olmalı; "
            "yalnızca harf, rakam, tire ve alt çizgi içermeli."
        )

    return STATE_DIRECTORY / f"conversation_{conversation_id}.json"

def load_state(conversation_id):
    state_path = get_state_path(conversation_id)

    if not state_path.exists():
        return create_empty_state()

    with state_path.open("r", encoding="utf-8") as file:
        return json.load(file)

def save_state(conversation_id, state):
    state_path = get_state_path(conversation_id)

    STATE_DIRECTORY.mkdir(parents=True, exist_ok=True)

    with state_path.open("w", encoding="utf-8") as file:
        json.dump(state, file, ensure_ascii=False, indent=2)