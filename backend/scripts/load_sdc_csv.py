import os
import json
import pandas as pd
import httpx
from typing import List, Dict, Any

"""
Usage:
  python scripts/load_sdc_csv.py --csv "D:/AI Ethics Stimulator/data/self_driving_synth.csv" --api "http://localhost:8000/api"
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
        csv_path = os.path.join("D:/AI Ethics Stimulator/data", "self_driving_synth.csv")
    return csv_path, api_base

def normalize_series(s: pd.Series):
    s = pd.to_numeric(s, errors='coerce').fillna(0.0)
    mn, mx = s.min(), s.max()
    rng = (mx - mn) if mx != mn else 1.0
    return (s - mn) / rng

def build_scenario_from_csv(csv_path: str) -> Dict[str, Any]:
    df = pd.read_csv(csv_path)
    ids = df['scenario_id'] if 'scenario_id' in df.columns else pd.Series([i for i in range(len(df))])
    p_age = df['passenger_age'] if 'passenger_age' in df.columns else pd.Series([0]*len(df))
    ped_age = df['pedestrian_age'] if 'pedestrian_age' in df.columns else pd.Series([0]*len(df))
    risk = df['risk_level'] if 'risk_level' in df.columns else pd.Series([0]*len(df))
    group = df['group'] if 'group' in df.columns else pd.Series(['unknown']*len(df))

    risk_norm = normalize_series(risk)

    entities: List[Dict[str, Any]] = []
    for i in range(len(df)):
        entities.append({
            "id": str(ids.iloc[i]),
            "passenger_age": float(pd.to_numeric(p_age.iloc[i], errors='coerce')),
            "pedestrian_age": float(pd.to_numeric(ped_age.iloc[i], errors='coerce')),
            "risk_level": float(pd.to_numeric(risk.iloc[i], errors='coerce')),
            "risk_level_norm": float(risk_norm.iloc[i]),
            "group": None if pd.isna(group.iloc[i]) else str(group.iloc[i])
        })

    scenario = {
        "type": "self_driving",
        "protected_attribute": "group",
        "entities": entities,
        "constraints": {"require_if": [], "disqualify_if": []},
        "scenario_name": "Self-Driving Car",
        "entity_type": "event",
        "attributes": ["passenger_age","pedestrian_age","risk_level","group"],
        # Minimize harm: utility features invert risk (we want lower risk) -> use (1 - risk_level)
        # We express via using risk_level but interpretation remains; utilitarian will pick lower risk if weights set appropriately.
        "metrics": {"utility_features": ["risk_level"], "fairness_protected": "group"},
        "rules": [
            # Example rule: avoid harming children group
            {"field": "group", "one_of_not": ["child"]}
        ],
        "default_params": {"top_k": 10, "weights": {"risk_level": -1.0}},
        "description": "Accident dilemmas balancing harm minimization and ethics"
    }
    return scenario


def register_scenario(api_base: str, scenario: Dict[str, Any]):
    payload = {"name": "Self-Driving Car", "type": "self_driving", "description": scenario.get("description"), "config": scenario}
    with httpx.Client(timeout=30) as client:
        r = client.post(f"{api_base}/scenarios", json=payload)
        if r.status_code != 409:
            r.raise_for_status()

def main():
    csv_path, api_base = parse_args()
    scenario = build_scenario_from_csv(csv_path)
    out = os.path.join(os.path.dirname(csv_path), 'self_driving_scenario.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(scenario, f, ensure_ascii=False)
    register_scenario(api_base, scenario)
    print("SDC_SCENARIO_REGISTERED")

if __name__ == '__main__':
    main()