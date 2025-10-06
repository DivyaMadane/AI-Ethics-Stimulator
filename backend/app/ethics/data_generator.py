from typing import Dict, Any

def hiring_demo_scenario() -> Dict[str, Any]:
    # Simple synthetic hiring scenario with protected attribute 'group'
    return {
        "type": "hiring",
        "protected_attribute": "group",
        "entities": [
            {"id": "A", "experience": 5, "test_score": 80, "group": "X", "utility": 0.7},
            {"id": "B", "experience": 3, "test_score": 85, "group": "Y", "utility": 0.6},
            {"id": "C", "experience": 6, "test_score": 70, "group": "X", "utility": 0.8},
            {"id": "D", "experience": 4, "test_score": 60, "group": "Y", "utility": 0.5},
        ],
        "constraints": {
            "require_if": [{"field": "experience", "one_of": [3,4,5,6,7]}],
            "disqualify_if": [{"field": "test_score", "one_of": []}]
        }
    }