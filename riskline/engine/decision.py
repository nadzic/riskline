from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Decision:
    action: str
    guidance: str


def decide_action(score: int) -> Decision:
    if score <= 35:
        return Decision(action="BUY", guidance="DCA-BUY (3 tranches) / Reduce leverage")
    if score >= 70:
        return Decision(action="REDUCE", guidance="Take profits / Reduce leverage")
    return Decision(action="HOLD", guidance="Hold spot / Avoid overtrading")
