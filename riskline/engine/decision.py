def decide_action(score: int) -> str:
    if score <= 35:
        return "BUY"
    if score >= 70:
        return "REDUCE"
    return "HOLD"
