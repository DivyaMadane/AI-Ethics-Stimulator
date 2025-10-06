from sqlalchemy.orm import Session
from sqlalchemy import select
from ..models import Run, Result
from typing import List, Dict

class RunService:
    @staticmethod
    def create_run(db: Session, scenario_id: int, frameworks: List[str], params: dict) -> Run:
        run = Run(scenario_id=scenario_id, requested_frameworks=frameworks, params=params)
        db.add(run)
        db.flush()
        return run

    @staticmethod
    def add_results(db: Session, run_id: int, results: List[Dict]):
        for r in results:
            db.add(Result(run_id=run_id,
                          framework=r["framework"],
                          decisions=r["decisions"],
                          metrics=r["metrics"],
                          explanation=r["explanation"]))
        db.flush()

    @staticmethod
    def get_run(db: Session, run_id: int) -> Run | None:
        return db.get(Run, run_id)

    @staticmethod
    def list_runs(db: Session) -> List[Run]:
        return list(db.scalars(select(Run).order_by(Run.created_at.desc())))