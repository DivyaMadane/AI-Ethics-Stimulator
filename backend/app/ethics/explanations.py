from typing import Dict, Any

def _percent(x: float) -> str:
    try:
        return f"{max(0.0, min(1.0, float(x)))*100:.0f}%"
    except Exception:
        return "0%"

def generate_explanation(framework: str, decisions: Dict[str, Any], metrics: Dict[str, Any], context: Dict[str, Any]) -> str:
    if framework == "utilitarian":
        avg = float(metrics.get('avg_utility', 0.0))
        total = float(metrics.get('total_utility', 0.0))
        msg = (
            f"Utilitarian prioritized overall performance. "
            f"Avg utility={avg:.2f}, total={total:.2f}. "
        )
        # Trade-off hint: if parity gap likely large per other contexts we can't see, provide generic caveat
        msg += "May reduce group balance if scores differ by group."
        return msg
    if framework == "fairness":
        gap = float(metrics.get('parity_gap', 0.0))
        fairness = 1 - gap
        msg = (
            f"Fairness emphasized balanced selection across groups. "
            f"Parity gap={gap:.3f} ({_percent(fairness)} fairness). "
            f"Trade-off: may slightly reduce average performance."
        )
        return msg
    if framework == "rule_based":
        rate = float(metrics.get('constraint_satisfaction_rate', 1.0))
        rules = context.get('applied_rules') or {}
        msg = (
            f"Rule-based enforced constraints {rules}. "
            f"Constraint satisfaction={_percent(rate)}. "
            f"Trade-off: may exclude borderline candidates."
        )
        return msg
    return "Executed framework-specific logic with computed metrics."
