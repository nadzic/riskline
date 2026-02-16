from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_state(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_state(path: str, state: dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(state, indent=2))
