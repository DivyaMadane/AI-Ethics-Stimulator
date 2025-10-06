from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime

# Pydantic v2 models
class ScenarioCreate(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    config: Dict[str, Any]

class ScenarioOut(BaseModel):
    id: int
    name: str
    type: str
    description: Optional[str]
    config: Dict[str, Any]
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class SimulateRequest(BaseModel):
    scenario_id: Optional[int] = Field(None, description="Existing scenario id")
    scenario_inline: Optional[Dict[str, Any]] = Field(None, description="Inline scenario if not using stored")
    frameworks: List[str] = Field(default_factory=lambda: ["utilitarian", "fairness", "rule_based"])
    params: Dict[str, Any] = Field(default_factory=dict)

class ResultOut(BaseModel):
    id: int
    framework: str
    decisions: Dict[str, Any]
    metrics: Dict[str, Any]
    explanation: str

    model_config = {
        "from_attributes": True
    }

class RunOut(BaseModel):
    id: int
    scenario_id: int
    requested_frameworks: List[str]
    params: Dict[str, Any] | None
    created_at: datetime
    results: List[ResultOut]

    model_config = {
        "from_attributes": True
    }