# AI Ethics Simulator

An interactive simulator to compare AI decisions under different ethical frameworks (Utilitarianism, Fairness-aware, Rule-based). Frontend: React + Tailwind + D3. Backend: FastAPI + SQLAlchemy (PostgreSQL).

## 1. Features
- Scenario templates (seeded with a Hiring Bias Demo)
- Ethics Engine: utilitarian, fairness-aware (demographic parity inspired), rule-based constraints
- Explanations, metrics, and comparative charts
- REST API with Pydantic models

## 2. Tech Stack
- Backend: FastAPI, SQLAlchemy, Pydantic v2
- DB: PostgreSQL (JSONB fields)
- Frontend: React (Vite), Tailwind CSS, D3.js
- Tests: pytest + FastAPI TestClient

## 3. Local Setup (Windows PowerShell)

### 3.1 Start PostgreSQL (Docker recommended)
```
pwsh path=null start=null
# In project root
docker compose up -d db
```

### 3.2 Backend
```
pwsh path=null start=null
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r backend/requirements.txt
# Configure .env if needed (copies example)
Copy-Item backend/.env.example backend/.env -Force
# Run API
uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir backend
```
Open http://localhost:8000/docs to inspect the API.

### 3.3 Frontend
```
pwsh path=null start=null
# Requires Node.js 18+
cd frontend
npm install
npm run dev
```
Open http://localhost:5173 and ensure the backend is reachable at http://localhost:8000.

## 4. Environment Variables
- DATABASE_URL: e.g. `postgresql+psycopg2://postgres:postgres@localhost:5432/ai_ethics_sim`
- Optionally set `VITE_API_BASE` in a `.env` file within `frontend/` to override API base URL.

## 5. API Quick Reference
- GET /api/health
- GET /api/scenarios
- POST /api/scenarios
- POST /api/simulate
- GET /api/runs
- GET /api/runs/{id}

## 6. Tests
```
pwsh path=null start=null
. .venv/Scripts/Activate.ps1
pytest -q backend
```

## 7. Notes
- The Ethics Engine modules are pluggable; add new frameworks in `backend/app/ethics/` and register in `FRAMEWORK_DISPATCH`.
- This project is designed for local demo and teaching; it avoids heavy ML training and focuses on transparent logic.