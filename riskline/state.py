from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class RiskState:
    last_alert_ts: int = 0
    last_regime: str = ""
    prev_oi: float | None = None
    prev_daily_close: float | None = None


def load_state(path: str) -> RiskState:
    p = Path(path)
    if not p.exists():
        return RiskState()
    data: dict[str, Any] = json.loads(p.read_text())
    return RiskState(
        last_alert_ts=int(data.get("last_alert_ts", 0)),
        last_regime=str(data.get("last_regime", "")),
        prev_oi=float(data["prev_oi"]) if data.get("prev_oi") is not None else None,
        prev_daily_close=(
            float(data["prev_daily_close"])
            if data.get("prev_daily_close") is not None
            else None
        ),
    )


def save_state(path: str, state: RiskState) -> None:
    Path(path).write_text(json.dumps(asdict(state), indent=2))


def compute_oi_delta_pct(prev_oi: float | None, current_oi: float | None) -> float | None:
    if prev_oi is None or current_oi is None or prev_oi == 0:
        return None
    return ((current_oi - prev_oi) / prev_oi) * 100.0


def should_send_alert(
    *,
    state: RiskState,
    current_regime: str,
    cooldown_hours: int,
    now_ts: int | None = None,
) -> tuple[bool, str]:
    now_ts = now_ts or int(time.time())
    if not state.last_regime:
        return True, "first_alert"
    if state.last_regime != current_regime:
        return True, "regime_flip"

    elapsed_seconds = now_ts - state.last_alert_ts
    if elapsed_seconds >= cooldown_hours * 3600:
        return True, "cooldown_elapsed"
    return False, "cooldown_active"
