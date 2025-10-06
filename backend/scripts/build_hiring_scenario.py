import csv
import json
import sys
import os
from typing import List, Dict, Any

# Usage: python build_hiring_scenario.py --data-dir D:\AI Ethics Stimulator\data --out D:\AI Ethics Stimulator\data\hiring_scenario.json
# This script scans the data directory for CSV files and attempts to transform a Kaggle HR dataset
# (e.g., arashnic/hr-analytics-job-change-of-data-scientists) into the simulator's scenario format.


def parse_experience(val: str) -> float:
    if val is None:
        return 0.0
    s = str(val).strip()
    if s == "" or s.lower() == "nan":
        return 0.0
    if s.startswith(">"):
        try:
            return float(s[1:]) + 1.0
        except Exception:
            return 21.0
    if s.startswith("<"):
        return 0.5
    try:
        return float(s)
    except Exception:
        return 0.0


def to_float(val: Any, default: float = 0.0) -> float:
    try:
        return float(val)
    except Exception:
        return default


def build_candidates_from_csv(csv_path: str) -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        idx = 0
        for row in reader:
            # Try common fields from the Kaggle dataset
            # Fallbacks will still produce a candidate list even if columns differ
            enrollee_id = row.get('enrollee_id') or row.get('id') or str(idx)
            name = row.get('name') or f"Candidate {enrollee_id}"
            experience = parse_experience(row.get('experience') or row.get('Experience') or row.get('years_experience'))
            # Use training_hours as a proxy for test_score if present; else try other numeric fields
            test_score = to_float(row.get('training_hours') or row.get('Training_hours') or row.get('test_score') or row.get('score') or 0)
            gender = row.get('gender') or row.get('Gender') or row.get('sex') or row.get('Sex') or "unknown"
            department = row.get('department') or row.get('Department') or row.get('dept') or row.get('Dept')
            education = row.get('education_level') or row.get('education') or row.get('Education')

            candidate = {
                "id": str(enrollee_id),
                "name": name,
                "experience": experience,
                "test_score": test_score,
                "gender": gender,
            }
            if department is not None:
                candidate["department"] = department
            if education is not None:
                candidate["education"] = education

            candidates.append(candidate)
            idx += 1
    return candidates


def main(argv: List[str]) -> int:
    # Parse args
    data_dir = None
    out_path = None
    args = iter(argv)
    for a in args:
        if a == '--data-dir':
            data_dir = next(args, None)
        elif a == '--out':
            out_path = next(args, None)
    if not data_dir or not out_path:
        print("Usage: python build_hiring_scenario.py --data-dir <dir> --out <file>")
        return 2

    # Find first CSV under data_dir
    csv_files = []
    for root, _, files in os.walk(data_dir):
        for fn in files:
            if fn.lower().endswith('.csv'):
                csv_files.append(os.path.join(root, fn))
    if not csv_files:
        print("No CSV files found in data directory.")
        return 1

    # Prefer files with 'train' or 'aug' in name for the chosen Kaggle dataset
    csv_files.sort(key=lambda p: ("train" not in os.path.basename(p).lower(), "aug" not in os.path.basename(p).lower(), os.path.basename(p).lower()))
    src = csv_files[0]
    print(f"Using CSV: {src}")

    candidates = build_candidates_from_csv(src)
    if not candidates:
        print("No candidates parsed from CSV.")
        return 1

    # Determine protected attribute preference: gender > department > none
    protected_attr = "gender" if any("gender" in c for c in [dict((k.lower(), v) for k, v in candidates[0].items())]) else ("department" if "department" in candidates[0] else None)
    if protected_attr is None:
        protected_attr = "gender"  # default to gender; values may be 'unknown'

    # Augment attributes list from candidate keys
    attribute_keys = set()
    for c in candidates:
        for k in ["gender", "education", "department", "experience", "test_score"]:
            if k in c:
                attribute_keys.add(k)
    attributes = sorted(list(attribute_keys))

    scenario = {
        # Engine-required keys
        "type": "hiring",
        "protected_attribute": protected_attr,
        "entities": candidates,
        "constraints": {"require_if": [], "disqualify_if": []},
        # UI/metadata keys requested
        "scenario_name": "Hiring",
        "entity_type": "candidate",
        "attributes": attributes,
        "metrics": {
            "utility_features": ["experience", "test_score"],
            "fairness_protected": protected_attr
        },
        "rules": [],
        # Store default params inside config for reference (UI uses its own defaults)
        "default_params": {"top_k": 10, "weights": {"experience": 0.5, "test_score": 0.5}},
        "description": "Simulation using full Kaggle HR dataset",
    }

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(scenario, f, ensure_ascii=False)
    print(f"Wrote scenario JSON to {out_path} with {len(candidates)} candidates.")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))