from typing import List, Dict, Any, Tuple

# Rule-based: Enforce hard constraints; if multiple candidates satisfy, use tie-breaker by score

def rule_based_decision(entities: List[Dict[str, Any]], common: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    constraints = common.get("constraints", {})
    params = common.get("params", {})
    disqualify_rules = constraints.get("disqualify_if", [])  # e.g., [{"field": "has_criminal_record", "equals": True}]
    require_rules = constraints.get("require_if", [])        # e.g., [{"field": "degree", "one_of": ["Masters","PhD"]}]

    def satisfies_require(e):
        for r in require_rules:
            field = r.get("field")
            if "equals" in r and e.get(field) != r.get("equals"):
                return False
            if "one_of" in r and e.get(field) not in set(r.get("one_of", [])):
                return False
        return True

    def violates_disqualify(e):
        for r in disqualify_rules:
            field = r.get("field")
            if "equals" in r and e.get(field) == r.get("equals"):
                return True
            if "one_of" in r and e.get(field) in set(r.get("one_of", [])):
                return True
        return False

    eligible = [e for e in entities if satisfies_require(e) and not violates_disqualify(e)]

    # Tie-break: by provided 'utility' or weighted numeric attributes
    weights = params.get("weights", {})
    def score(e):
        if "utility" in e:
            return float(e["utility"])
        s = 0.0
        for k, w in weights.items():
            if k in e and isinstance(e[k], (int, float)):
                s += w * float(e[k])
        return s

    eligible_sorted = sorted(eligible, key=score, reverse=True)
    k = int(params.get("top_k", 1))
    selected = eligible_sorted[:k]

    decisions = {
        "selected_ids": [e.get("id") for e in selected],
        "eligible_count": len(eligible),
        "disqualified_count": len(entities) - len(eligible)
    }

    # Metrics: constraint satisfaction rate
    metrics = {
        "constraint_satisfaction_rate": (len(selected) / max(1, k)),
        "eligibility_rate": (len(eligible) / max(1, len(entities)))
    }

    context = {"applied_rules": {"require_if": require_rules, "disqualify_if": disqualify_rules}}
    return decisions, metrics, context