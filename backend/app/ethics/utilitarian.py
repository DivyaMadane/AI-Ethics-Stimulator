from typing import List, Dict, Any, Tuple
import numpy as np

# Simple utilitarian logic: select option(s) maximizing aggregate utility
# Each entity is expected to have a 'utility' score or attributes with weights in params

def utilitarian_decision(entities: List[Dict[str, Any]], common: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    params = common.get("params", {})
    weights = params.get("weights", {})
    util_feats = common.get("utility_features", []) or ["experience","test_score"]

    # Precompute normalized features list per entity
    scores = []
    for e in entities:
        if "utility" in e:
            u = float(e["utility"]) 
        else:
            # Weighted sum across declared utility features; fallback to equal weights
            vals = []
            ws = []
            for feat in util_feats:
                norm_key = f"{feat}_norm"
                val = e.get(norm_key, e.get(feat, 0.0))
                vals.append(float(val))
                w = float(weights.get(feat, 0.0)) if feat in weights else np.nan
                ws.append(w)
            if all(np.isnan(ws)):
                # no matching weights provided; use equal weights
                wnorm = np.ones(len(vals)) / max(1, len(vals))
            else:
                # replace NaN with zero and normalize if sum>0, else equal
                ws = np.nan_to_num(ws, nan=0.0)
                s = ws.sum()
                wnorm = (ws / s) if s > 0 else (np.ones(len(vals)) / max(1, len(vals)))
            u = float(np.dot(wnorm, np.asarray(vals)))
        scores.append({"id": e.get("id"), "score": u, "group": e.get(common.get("protected_attribute"))})

    k = max(1, int(params.get("top_k", 1)))
    sorted_scores = sorted(scores, key=lambda x: x["score"], reverse=True)
    selected = sorted_scores[:k]

    decisions = {
        "selected_ids": [s["id"] for s in selected],
        "ranking": sorted_scores
    }

    metrics = {
        "total_utility": sum(s["score"] for s in selected),
        "avg_utility": (sum(s["score"] for s in selected) / max(1, len(selected))) if selected else 0.0,
    }

    context = {"weights": weights}
    return decisions, metrics, context
