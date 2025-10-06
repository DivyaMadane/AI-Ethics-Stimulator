from typing import Dict, Any, List, Tuple
from statistics import mean
from .utilitarian import utilitarian_decision
from .fairness import fairness_decision
from .rule_based import rule_based_decision
from .explanations import generate_explanation
from .analyzer import analyze_results

FRAMEWORK_DISPATCH = {
    "utilitarian": utilitarian_decision,
    "fairness": fairness_decision,
    "rule_based": rule_based_decision,
}

def _min_max(values: List[float]) -> Tuple[float, float]:
    if not values:
        return 0.0, 1.0
    return min(values), max(values) if max(values) != min(values) else (min(values), min(values) + 1.0)

def _normalize_entities(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Ensure numeric fields and normalize to [0,1]
    exps = []
    tests = []
    for e in entities:
        exp = e.get("experience")
        ts = e.get("test_score") or e.get("training_hours")
        try:
            exps.append(float(exp) if exp is not None else 0.0)
        except Exception:
            exps.append(0.0)
        try:
            tests.append(float(ts) if ts is not None else 0.0)
        except Exception:
            tests.append(0.0)
    mn_exp, mx_exp = (min(exps), max(exps)) if exps else (0.0, 1.0)
    mn_ts, mx_ts = (min(tests), max(tests)) if tests else (0.0, 1.0)
    rng_exp = (mx_exp - mn_exp) or 1.0
    rng_ts = (mx_ts - mn_ts) or 1.0

    normed = []
    for i, e in enumerate(entities):
        exp = exps[i] if i < len(exps) else 0.0
        ts = tests[i] if i < len(tests) else 0.0
        e2 = dict(e)
        e2["experience_norm"] = (exp - mn_exp) / rng_exp
        e2["test_score_norm"] = (ts - mn_ts) / rng_ts
        # Ensure categorical fields exist (fallbacks)
        if "gender" not in e2:
            e2["gender"] = e2.get("Gender") or "unknown"
        if "department" not in e2:
            e2["department"] = e2.get("dept") or e2.get("Department") or None
        normed.append(e2)
    return normed

def run_simulation(scenario: Dict[str, Any], frameworks: List[str], params: Dict[str, Any]) -> Dict[str, Any]:
    results = []

    # Normalize inputs
    scenario_type = scenario.get("type")
    entities_raw = scenario.get("entities", [])
    constraints = scenario.get("constraints", {})
    protected_attribute = scenario.get("protected_attribute") or "gender"

    entities = _normalize_entities(entities_raw)

    utility_features = []
    try:
        utility_features = list(scenario.get("metrics", {}).get("utility_features", []))
    except Exception:
        utility_features = []

    common = {
        "scenario_type": scenario_type,
        "constraints": constraints,
        "protected_attribute": protected_attribute,
        "utility_features": utility_features,
        "params": params,
    }

    for fw in frameworks:
        decision_func = FRAMEWORK_DISPATCH.get(fw)
        if decision_func is None:
            continue
        decisions, metrics, context = decision_func(entities, common)
        explanation = generate_explanation(fw, decisions, metrics, context)
        results.append({
            "framework": fw,
            "decisions": decisions,
            "metrics": metrics,
            "explanation": explanation
        })

    summary = analyze_results(results)
    return {"results": results, "summary": summary}
