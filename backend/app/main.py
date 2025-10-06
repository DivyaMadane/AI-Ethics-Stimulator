from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base
from .api.routes import router
from .services.scenarios import ScenarioService
from .ethics.data_generator import hiring_demo_scenario
from sqlalchemy.orm import Session

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Seed a demo scenario if not present
    from .database import SessionLocal
    with SessionLocal() as session:  # type: Session
        if not ScenarioService.get_by_name(session, "Hiring Bias Demo"):
            scen = hiring_demo_scenario()
            ScenarioService.create(session, name="Hiring Bias Demo", type=scen.get("type"), description="Synthetic hiring scenario with protected groups", config=scen)
            session.commit()

app.include_router(router, prefix="/api")