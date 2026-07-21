session_store: dict[str, list[float]] = {}

def record_and_check_escalation(session_id: str, risk_score: float):
    if not session_id:
        return {"escalation_flag": False, "trend": "no_session"}

    history = session_store.setdefault(session_id, [])
    history.append(risk_score)

    if len(history) < 2:
        return {"escalation_flag": False, "trend": "first_message", "history": history}

    escalating = history[-1] > history[-2] and history[-1] >= 60
    trend = "escalating" if escalating else "stable_or_declining"

    return {
        "escalation_flag": escalating,
        "trend": trend,
        "history": history
    }