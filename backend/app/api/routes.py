from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from sqlalchemy import select
from ..schemas import ScenarioCreate, ScenarioOut, SimulateRequest, RunOut, ResultOut
from ..database import get_session
from ..models import Scenario, Run, Result
from ..services.scenarios import ScenarioService
from ..services.runs import RunService
from ..ethics.runner import run_simulation

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/scenarios", response_model=List[ScenarioOut])
def list_scenarios(session=Depends(get_session)):
    return ScenarioService.get_all(session)

@router.post("/scenarios", response_model=ScenarioOut)
def create_scenario(payload: ScenarioCreate, session=Depends(get_session)):
    if ScenarioService.get_by_name(session, payload.name):
        raise HTTPException(status_code=409, detail="Scenario name already exists")
    scen = ScenarioService.create(session, payload.name, payload.type, payload.description, payload.config)
    return scen

@router.get("/scenarios/{scenario_id}", response_model=ScenarioOut)
def get_scenario(scenario_id: int, session=Depends(get_session)):
    scen = ScenarioService.get_by_id(session, scenario_id)
    if not scen:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scen

@router.post("/simulate")
def simulate(req: SimulateRequest, session=Depends(get_session)):
    # Resolve scenario
    if req.scenario_id is not None:
        scen_obj = ScenarioService.get_by_id(session, req.scenario_id)
        if not scen_obj:
            raise HTTPException(status_code=404, detail="Scenario not found")
        scenario = scen_obj.config | {"type": scen_obj.type}
        scenario["name"] = scen_obj.name
    elif req.scenario_inline is not None:
        scenario = req.scenario_inline
    else:
        raise HTTPException(status_code=400, detail="Provide scenario_id or scenario_inline")

    # Find previous run for comparison (before creating new run)
    prev_run = session.scalars(select(Run).where(Run.scenario_id == scen_obj.id).order_by(Run.created_at.desc())).first() if req.scenario_id else None

    sim_out = run_simulation(scenario, req.frameworks, req.params)

    # Persist run and results
    if req.scenario_id is None:
        # For inline scenario, store a transient scenario entry for traceability
        scen_obj = ScenarioService.create(session, scenario.get("name", "inline"), scenario.get("type", "custom"), scenario.get("description"), scenario)

    run = RunService.create_run(session, scen_obj.id, req.frameworks, req.params)
    RunService.add_results(session, run.id, sim_out["results"])

    # Comparison mapping
    def fairness_value(m):
        gap = float(m.get("parity_gap", 0.0))
        return 1.0 - gap

    comparison = {"deltas": {}, "text": []}
    if prev_run and prev_run.results:
        # Build prev map
        prev_map = {res.framework: res.metrics for res in prev_run.results}
        for r in sim_out["results"]:
            fw = r["framework"]
            cur_m = r.get("metrics", {})
            prev_m = prev_map.get(fw, {})
            if fw == "utilitarian":
                cur = float(cur_m.get("avg_utility", 0.0))
                prev = float(prev_m.get("avg_utility", 0.0))
                delta = cur - prev
                comparison["deltas"][fw] = {"avg_utility": delta}
                comparison["text"].append(f"Utilitarian performance changed by {delta:+.2f} vs previous run.")
            elif fw == "fairness":
                cur = fairness_value(cur_m)
                prev = fairness_value(prev_m)
                delta = cur - prev
                comparison["deltas"][fw] = {"fairness": delta}
                comparison["text"].append(f"Fairness changed by {delta*100:+.0f}% vs previous run.")
            elif fw == "rule_based":
                cur = float(cur_m.get("constraint_satisfaction_rate", 1.0))
                prev = float(prev_m.get("constraint_satisfaction_rate", 1.0))
                delta = cur - prev
                comparison["deltas"][fw] = {"constraint_satisfaction_rate": delta}
                comparison["text"].append(f"Rule compliance changed by {delta*100:+.0f}% vs previous run.")

    # Scenario-specific labels
    st = scenario.get("type")
    if st == "hiring":
        labels = {
            "utilitarian": "Performance",
            "fairness": "Fairness",
            "rule_based": "Rule Compliance"
        }
        descriptions = {
            "utilitarian": "Higher means stronger overall candidate performance.",
            "fairness": "Higher means more equal selection across gender/department.",
            "rule_based": "Higher means more selections satisfied policy constraints."
        }
    elif st == "healthcare":
        labels = {
            "utilitarian": "Accuracy",
            "fairness": "Bias Mitigation",
            "rule_based": "Patient Safety"
        }
        descriptions = {
            "utilitarian": "Higher means better clinical prioritization accuracy.",
            "fairness": "Higher means less disparity across income groups.",
            "rule_based": "Higher means safer allocations under rules."
        }
    else:
        labels = {
            "utilitarian": "Safety Score",
            "fairness": "Ethical Decision Balance",
            "rule_based": "Law Compliance"
        }
        descriptions = {
            "utilitarian": "Higher means lower overall harm risk.",
            "fairness": "Higher means balanced choices across groups.",
            "rule_based": "Higher means more decisions follow safety laws/constraints."
        }

    # Build response
    session.refresh(run)
    payload = {
        "run": RunOut.model_validate({
            "id": run.id,
            "scenario_id": run.scenario_id,
            "requested_frameworks": run.requested_frameworks,
            "params": run.params,
            "created_at": run.created_at,
            "results": [
                {
                    "id": res.id,
                    "framework": res.framework,
                    "decisions": res.decisions,
                    "metrics": res.metrics,
                    "explanation": res.explanation,
                } for res in run.results
            ]
        }).model_dump(mode="json"),
        "summary": sim_out.get("summary", {}),
        "labels": labels,
        "descriptions": descriptions,
        "comparison": comparison
    }
    return JSONResponse(payload)

@router.get("/runs", response_model=List[RunOut])
def list_runs(session=Depends(get_session)):
    runs = RunService.list_runs(session)
    payload = []
    for run in runs:
        payload.append(RunOut.model_validate({
            "id": run.id,
            "scenario_id": run.scenario_id,
            "requested_frameworks": run.requested_frameworks,
            "params": run.params,
            "created_at": run.created_at,
            "results": [
                {
                    "id": res.id,
                    "framework": res.framework,
                    "decisions": res.decisions,
                    "metrics": res.metrics,
                    "explanation": res.explanation,
                } for res in run.results
            ]
        }))
    return payload

@router.get("/runs/{run_id}", response_model=RunOut)
def get_run(run_id: int, session=Depends(get_session)):
    run = session.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunOut.model_validate({
        "id": run.id,
        "scenario_id": run.scenario_id,
        "requested_frameworks": run.requested_frameworks,
        "params": run.params,
        "created_at": run.created_at,
        "results": [
            {
                "id": res.id,
                "framework": res.framework,
                "decisions": res.decisions,
                "metrics": res.metrics,
                "explanation": res.explanation,
            } for res in run.results
        ]
    })