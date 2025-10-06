from typing import List, Dict, Any

def analyze_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Provide a compact comparison summary across frameworks
    summary = {
        "frameworks": [r["framework"] for r in results],
        "selected_ids": {r["framework"]: r["decisions"].get("selected_ids", []) for r in results},
        "metrics": {r["framework"]: r.get("metrics", {}) for r in results}
    }
    return summary
