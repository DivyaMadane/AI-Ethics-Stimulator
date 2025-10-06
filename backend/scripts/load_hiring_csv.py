import os
import json
import pandas as pd
import numpy as np
import httpx
from typing import List, Dict, Any

"""
Usage:
  python scripts/load_hiring_csv.py --csv "D:/AI Ethics Stimulator/data/hiring.csv" --api "http://localhost:8000/api"

Reads hiring.csv, produces a normalized scenario JSON and registers it with the backend.
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
        # default
        csv_path = os.path.join("D:/AI Ethics Stimulator/data", "hiring.csv")
    return csv_path, api_base


def normalize_series(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors='coerce').fillna(0.0)
    mn = s.min()
    mx = s.max()
    rng = (mx - mn) if mx != mn else 1.0
    return (s - mn) / rng


def build_scenario_from_csv(csv_path: str) -> Dict[str, Any]:
    df = pd.read_csv(csv_path)

    # Candidate id/name
    if 'id' in df.columns:
        ids = df['id'].astype(str)
    elif 'enrollee_id' in df.columns:
        ids = df['enrollee_id'].astype(str)
    else:
        ids = pd.Series([str(i) for i in range(len(df))])

    names = df['name'] if 'name' in df.columns else pd.Series([f"Candidate {i}" for i in range(len(df))])

    # Numeric fields
    exp_raw = df['experience'] if 'experience' in df.columns else (df['years_experience'] if 'years_experience' in df.columns else pd.Series([0]*len(df)))
    test_raw = df['test_score'] if 'test_score' in df.columns else (df['training_hours'] if 'training_hours' in df.columns else pd.Series([0]*len(df)))

    exp_norm = normalize_series(exp_raw)
    test_norm = normalize_series(test_raw)

    # Categoricals
    gender = df['gender'] if 'gender' in df.columns else (df['Gender'] if 'Gender' in df.columns else pd.Series(['unknown']*len(df)))
    dept = df['department'] if 'department' in df.columns else (df['Department'] if 'Department' in df.columns else pd.Series([None]*len(df)))

    entities: List[Dict[str, Any]] = []
    for i in range(len(df)):
        entities.append({
            "id": str(ids.iloc[i]),
            "name": str(names.iloc[i]),
            "experience": float(pd.to_numeric(exp_raw.iloc[i], errors='coerce')) if i < len(exp_raw) else 0.0,
            "test_score": float(pd.to_numeric(test_raw.iloc[i], errors='coerce')) if i < len(test_raw) else 0.0,
            "experience_norm": float(exp_norm.iloc[i]),
            "test_score_norm": float(test_norm.iloc[i]),
            "gender": None if pd.isna(gender.iloc[i]) else str(gender.iloc[i]),
            "department": None if pd.isna(dept.iloc[i]) else str(dept.iloc[i]),
        })

    scenario = {
        "type": "hiring",
        "protected_attribute": "gender",
        "entities": entities,
        "constraints": {"require_if": [], "disqualify_if": []},
        "scenario_name": "Hiring",
        "entity_type": "candidate",
        "attributes": ["gender","department","experience","test_score"],
        "metrics": {"utility_features": ["experience","test_score"], "fairness_protected": "gender"},
        "rules": [],
        "default_params": {"top_k": 10, "weights": {"experience": 0.5, "test_score": 0.5}},
        "description": "Simulation using full hiring.csv dataset",
    }
    return scenario


def register_scenario(api_base: str, scenario: Dict[str, Any]):
    payload = {
        "name": "Hiring",
        "type": "hiring",
        "description": scenario.get("description"),
        "config": scenario
    }
    with httpx.Client(timeout=30) as client:
        r = client.post(f"{api_base}/scenarios", json=payload)
        if r.status_code == 409:
            # already exists; ok
            return
        r.raise_for_status()


def main():
    csv_path, api_base = parse_args()
    scenario = build_scenario_from_csv(csv_path)
    # Write JSON for traceability
    out = os.path.join(os.path.dirname(csv_path), 'hiring_scenario.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(scenario, f, ensure_ascii=False)
    try:
        register_scenario(api_base, scenario)
        print("SCENARIO_REGISTERED")
    except Exception as e:
        print(f"REGISTER_FAILED: {e}")

if __name__ == '__main__':
    main()