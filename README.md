# AI Ethics Simulator

An interactive, scenario-adaptive simulator that compares AI decisions under multiple ethical frameworks (Utilitarian, Fairness, Rule-based) across Hiring, Healthcare, and Self-Driving Car domains. Built for professional demos: clear visuals, intuitive explanations, and exportable results.

## 1. Features
- Three scenarios with synthetic datasets (≥200 records each): Hiring, Healthcare, Self-Driving Car
- Frameworks: Utilitarian (performance), Fairness (parity/balance), Rule-based (constraints)
- Scenario-aware metrics and labels
  - Hiring: Performance, Fairness, Rule Compliance
  - Healthcare: Accuracy, Bias Mitigation, Patient Safety
  - Self-Driving: Safety Score, Ethical Decision Balance, Law Compliance
- Visuals: animated metric bars, trade-off bar chart, radar chart, comparison badges, summary insights
- Explanations: per-framework natural language rationale + comparison deltas vs previous run
- Export: CSV of results

## 2. Tech Stack
- Backend: FastAPI, SQLAlchemy, Pydantic v2, pandas, numpy
- DB: SQLite (default) or PostgreSQL
- Frontend: React (Vite), Tailwind CSS, D3.js, Chart.js (react-chartjs-2), canvas-confetti
- Tests: pytest + FastAPI TestClient

## 3. Local Setup (Windows PowerShell)

Quick start (both services)
- Backend (port 8000) and Frontend (port 5173)

Backend (PowerShell)
- cd "D:\AI Ethics Stimulator\backend"
- python -m venv .venv
- . .venv\Scripts\Activate.ps1
- pip install -r requirements.txt
- $env:DATABASE_URL = "sqlite+pysqlite:///./dev.db"
- uvicorn app.main:app --host 0.0.0.0 --port 8000

Frontend (new PowerShell tab)
- cd "D:\AI Ethics Stimulator\frontend"
- $env:ComSpec = "C:\\Windows\\System32\\cmd.exe"
- echo VITE_API_BASE=http://localhost:8000/api > .env
- npm install
- npm run dev

Then open http://localhost:5173

### 3.1 Backend (SQLite default)
```
pwsh path=null start=null
cd "D:\AI Ethics Stimulator\backend"
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DATABASE_URL = "sqlite+pysqlite:///./dev.db"
python scripts\generate_datasets.py
# Optional: load your own hiring.csv
# python scripts\load_hiring_csv.py --csv "D:\AI Ethics Stimulator\data\hiring.csv" --api "http://localhost:8000/api"
# Register synth scenarios
python scripts\load_healthcare_csv.py --csv "D:\AI Ethics Stimulator\data\healthcare_synth.csv" --api "http://localhost:8000/api"
python scripts\load_sdc_csv.py --csv "D:\AI Ethics Stimulator\data\self_driving_synth.csv" --api "http://localhost:8000/api"
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Open http://localhost:8000/docs to inspect the API.

### 3.2 Frontend
```
pwsh path=null start=null
cd "D:\AI Ethics Stimulator\frontend"
$env:ComSpec = "C:\\Windows\\System32\\cmd.exe"
echo VITE_API_BASE=http://localhost:8000/api > .env
npm install
npm run dev
```
Open http://localhost:5173 and ensure the backend is reachable at http://localhost:8000.

## 4. Scenarios and Metrics
- Hiring
  - Metrics: Performance (avg utility), Fairness (1 - parity gap), Rule Compliance (constraint satisfaction)
  - Example insight: “Fairness selected more minority candidates reducing parity gap by 8%.”
- Healthcare
  - Metrics: Accuracy (avg utility over severity/priority), Bias Mitigation (1 - parity gap by income), Patient Safety (rules)
  - Example insight: “Rule-based ensured high-priority patients were never deprioritized below threshold.”
- Self-Driving Car
  - Metrics: Safety Score (lower risk), Ethical Decision Balance, Law Compliance
  - Example insight: “Utilitarian minimized harm but Law Compliance decreased.”

## 5. How Decisions Are Compared
- Utilitarian: Maximizes weighted, normalized attributes per scenario (e.g., severity/priority or risk)
- Fairness: Demographic parity-inspired selection across protected groups; measures parity gap
- Rule-based: Enforces explicit constraints; computes constraint satisfaction rate
- Comparison: Deltas vs previous run (e.g., “Fairness improved by +8%”) and summary insight with badges

## 6. API Quick Reference
- GET /api/health
- GET /api/scenarios
- POST /api/scenarios
- POST /api/simulate
- GET /api/runs
- GET /api/runs/{id}

## 7. Screenshots (placeholders)
- /docs/screenshots/hiring_dashboard.png
- /docs/screenshots/healthcare_dashboard.png
- /docs/screenshots/self_driving_dashboard.png

## 8. Notes

Troubleshooting
- Frontend “Failed to fetch” on run: ensure backend is running and that VITE_API_BASE matches http://localhost:8000/api; refresh the browser.
- 500 errors on /api/simulate: fixed by serializing datetimes; if you still see errors, restart backend and retry.
- Node/npm issues on Windows: set $env:ComSpec to cmd.exe before npm run dev.
- Hide demo scenario: the UI filters out “Hiring Bias Demo” in the scenario selector.
- The Ethics Engine modules are pluggable; add new frameworks in `backend/app/ethics/` and register in `FRAMEWORK_DISPATCH`.
- This project focuses on transparent, educational simulations — not production ML.
