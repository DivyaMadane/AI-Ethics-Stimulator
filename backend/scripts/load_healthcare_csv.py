import os
import json
import pandas as pd
import httpx
from typing import List, Dict, Any

"""
Usage:
  python scripts/load_healthcare_csv.py --csv "D:/AI Ethics Stimulator/data/healthcare_synth.csv" --api "http://localhost:8000/api"
"""

def parse_args():
    import sys
    args = iter(sys.argv[1:])
    csv_path = None
    api_base = "http://localhost:8000/api"
    for a in args:
        if a == "--csv":
            csv_path = next(args, None)
        elif a == "--api":
            api_base = next(args, api_base)
    if not csv_path:
        csv_path = os.path.join("D:/AI Ethics Stimulator/data", "healthcare_synth.csv")
    return csv_path, api_base

def normalize_series(s: pd.Series):
    s = pd.to_numeric(s, errors='coerce').fillna(0.0)
    mn, mx = s.min(), s.max()
    rng = (mx - mn) if mx != mn else 1.0
    return (s - mn) / rng

def build_scenario_from_csv(csv_path: str) -> Dict[str, Any]:
    df = pd.read_csv(csv_path)
    # IDs & values
    ids = df['patient_id'] if 'patient_id' in df.columns else pd.Series([i for i in range(len(df))])
    age = df['age'] if 'age' in df.columns else pd.Series([0]*len(df))
    severity = df['severity'] if 'severity' in df.columns else pd.Series([0]*len(df))
    income = df['income_group'] if 'income_group' in df.columns else pd.Series(['unknown']*len(df))
    cost = df['treatment_cost'] if 'treatment_cost' in df.columns else pd.Series([0]*len(df))
    priority = df['priority'] if 'priority' in df.columns else pd.Series([0]*len(df))

    entities: List[Dict[str, Any]] = []
    sev_norm = normalize_series(severity)
    pri_norm = normalize_series(priority)
    for i in range(len(df)):
        entities.append({
            "id": str(ids.iloc[i]),
            "age": float(pd.to_numeric(age.iloc[i], errors='coerce')),
            "severity": float(pd.to_numeric(severity.iloc[i], errors='coerce')),
            "priority": float(pd.to_numeric(priority.iloc[i], errors='coerce')),
            "treatment_cost": float(pd.to_numeric(cost.iloc[i], errors='coerce')),
            "severity_norm": float(sev_norm.iloc[i]),
            "priority_norm": float(pri_norm.iloc[i]),
            "income_group": None if pd.isna(income.iloc[i]) else str(income.iloc[i])
        })

    scenario = {
        "type": "healthcare",
        "protected_attribute": "income_group",
        "entities": entities,
        "constraints": {"require_if": [], "disqualify_if": []},
        "scenario_name": "Healthcare",
        "entity_type": "patient",
        "attributes": ["age","severity","priority","income_group"],
        "metrics": {"utility_features": ["severity","priority"], "fairness_protected": "income_group"},
        "rules": [
            # Example rule: prioritize patients with priority >= 0.5
            {"field": "priority_norm", "min": 0.5}
        ],
        "default_params": {"top_k": 20, "weights": {"severity": 0.6, "priority": 0.4}},
        "description": "Resource allocation with fairness by income group"
    }
    return scenario


def register_scenario(api_base: str, scenario: Dict[str, Any]):
    payload = {"name": "Healthcare", "type": "healthcare", "description": scenario.get("description"), "config": scenario}
    with httpx.Client(timeout=30) as client:
        r = client.post(f"{api_base}/scenarios", json=payload)
        if r.status_code != 409:
            r.raise_for_status()

def main():
    csv_path, api_base = parse_args()
    scenario = build_scenario_from_csv(csv_path)
    out = os.path.join(os.path.dirname(csv_path), 'healthcare_scenario.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(scenario, f, ensure_ascii=False)
    register_scenario(api_base, scenario)
    print("HEALTHCARE_SCENARIO_REGISTERED")

if __name__ == '__main__':
    main()