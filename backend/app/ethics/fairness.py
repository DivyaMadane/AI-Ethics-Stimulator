from typing import List, Dict, Any, Tuple
from collections import defaultdict
import numpy as np

# Fairness-aware selection: approximate demographic parity by balancing selection rates across groups

def fairness_decision(entities: List[Dict[str, Any]], common: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    params = common.get("params", {})
    protected_attr = common.get("protected_attribute")
    target_selection = max(1, int(params.get("top_k", 1)))
    weights = params.get("weights", {"experience": 0.5, "test_score": 0.5})

    # Score can be provided; otherwise use normalized weighted sum
    groups = defaultdict(list)
    for e in entities:
        grp = e.get(protected_attr, "unknown")
        base = e.get("utility")
        if base is None:
            exp = e.get("experience_norm", e.get("experience", 0.0))
            ts = e.get("test_score_norm", e.get("test_score", 0.0))
            base = weights.get("experience", 0.0) * float(exp) + weights.get("test_score", 0.0) * float(ts)
        score = float(base)
        groups[grp].append({"id": e.get("id"), "score": score, "entity": e})

    # Round-robin across groups based on descending score to approximate parity
    for g in groups:
        groups[g] = sorted(groups[g], key=lambda x: x["score"], reverse=True)

    pointers = {g:0 for g in groups}
    selected = []
    while len(selected) < target_selection and any(pointers[g] < len(groups[g]) for g in groups):
        for g in groups:
            if pointers[g] < len(groups[g]) and len(selected) < target_selection:
                selected.append(groups[g][pointers[g]])
                pointers[g] += 1

    decisions = {
        "selected_ids": [s["id"] for s in selected],
        "selection_by_group": {g: [x["id"] for x in groups[g][:pointers[g]]] for g in groups}
    }

    selection_counts = {g: pointers[g] for g in groups}
    group_sizes = {g: len(groups[g]) for g in groups}
    selection_rates = {g: (selection_counts[g] / max(1, group_sizes[g])) for g in groups}
    rates = list(selection_rates.values())
    parity_gap = (max(rates) - min(rates)) if rates else 0.0

    metrics = {
        "selection_rates": selection_rates,
        "parity_gap": parity_gap,
    }

    context = {"protected_attr": protected_attr}
    return decisions, metrics, context
