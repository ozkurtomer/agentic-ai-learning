import json
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = Path(__file__).parent / "events.jsonl"

def log_event(conversation_id, request_id, event_type, data):
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "conversation_id": conversation_id,
        "request_id": request_id,
        "event_type": event_type,
        "data": data
    }

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(
            json.dumps(event, ensure_ascii=False) + "\n"
        )