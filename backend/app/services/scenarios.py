from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
from ..models import Scenario

class ScenarioService:
    @staticmethod
    def get_all(db: Session):
        return list(db.scalars(select(Scenario).order_by(Scenario.created_at.desc())))

    @staticmethod
    def get_by_id(db: Session, scenario_id: int) -> Optional[Scenario]:
        return db.get(Scenario, scenario_id)

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Scenario]:
        stmt = select(Scenario).where(Scenario.name == name)
        return db.scalars(stmt).first()

    @staticmethod
    def create(db: Session, name: str, type: str, description: str | None, config: dict) -> Scenario:
        scen = Scenario(name=name, type=type, description=description, config=config)
        db.add(scen)
        db.flush()  # populate id
        return scen