from datetime import datetime
from pathlib import Path
import json


class EventDispatcher:
    EVENT_LOG = Path("metadata") / "event_log.jsonl"

    @staticmethod
    def emit(event_type: str, payload: dict):
        event = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": payload,
        }

        with open(EventDispatcher.EVENT_LOG, "a") as f:
            f.write(json.dumps(event) + "\n")

        print(f"[EVENT] {event_type}")
