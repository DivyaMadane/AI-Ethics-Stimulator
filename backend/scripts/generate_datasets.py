import os
import numpy as np
import pandas as pd

OUT_DIR = r"D:\AI Ethics Stimulator\data"

np.random.seed(42)

os.makedirs(OUT_DIR, exist_ok=True)

# 1) Hiring dataset (bias: majority group and certain departments score higher)
N = 200
candidate_id = np.arange(N)
gender = np.random.choice(["Male","Female"], size=N, p=[0.6,0.4])
department = np.random.choice(["Sales","Research & Development","Human Resources"], size=N, p=[0.4,0.5,0.1])
experience = np.clip(np.random.normal(loc=5, scale=2, size=N), 0, 15)
test_score_base = np.clip(np.random.normal(loc=70, scale=12, size=N), 30, 100)
# Inject bias: majority group + R&D get slight boost
boost = (gender == "Male") * 3 + (department == "Research & Development") * 4
test_score = np.clip(test_score_base + boost, 30, 100)
# Group label
group = np.where(gender == "Male", "majority", "minority")
# Simulate hired labels (not used by engine but good for display)
hired = (0.5*experience + 0.5*(test_score/10) + (gender=="Male")*0.5 + (department=="Research & Development")*0.5) > 11
hiring_df = pd.DataFrame({
    "id": candidate_id,
    "name": [f"Candidate {i}" for i in candidate_id],
    "gender": gender,
    "department": department,
    "experience": experience.round(2),
    "test_score": test_score.round(1),
    "group": group,
    "hired": hired.astype(int)
})
hiring_csv = os.path.join(OUT_DIR, "hiring_synth.csv")
hiring_df.to_csv(hiring_csv, index=False)

# 2) Healthcare dataset (bias: low-income get under-prioritized)
N2 = 200
patient_id = np.arange(N2)
age = np.clip(np.random.normal(50, 18, N2), 0, 100)
severity = np.clip(np.random.normal(0.6, 0.2, N2), 0, 1)
income_group = np.random.choice(["low","middle","high"], size=N2, p=[0.3,0.5,0.2])
treatment_cost = np.clip(np.random.normal(5000, 2000, N2), 500, 20000)
priority = np.clip(severity + np.random.normal(0,0.1,N2) + (income_group=="high")*0.05 - (income_group=="low")*0.05, 0, 1)
healthcare_df = pd.DataFrame({
    "patient_id": patient_id,
    "age": age.round(1),
    "severity": severity.round(3),
    "income_group": income_group,
    "treatment_cost": treatment_cost.round(0),
    "priority": priority.round(3)
})
health_csv = os.path.join(OUT_DIR, "healthcare_synth.csv")
healthcare_df.to_csv(health_csv, index=False)

# 3) Self-Driving Car dataset (bias: adult considered more often than elderly/child in risk calculations)
N3 = 200
scenario_id = np.arange(N3)
passenger_age = np.clip(np.random.normal(35, 12, N3), 0, 90)
pedestrian_age = np.clip(np.random.normal(30, 20, N3), 0, 90)
risk_level = np.clip(np.random.beta(2,5,size=N3), 0, 1)
category = np.random.choice(["child","adult","elderly"], size=N3, p=[0.2,0.6,0.2])
# Decision baseline (not used by engine; for display)
decision_made = np.random.choice(["protect_passenger","protect_pedestrian"], size=N3, p=[0.5,0.5])
sdc_df = pd.DataFrame({
    "scenario_id": scenario_id,
    "passenger_age": passenger_age.round(1),
    "pedestrian_age": pedestrian_age.round(1),
    "risk_level": risk_level.round(3),
    "group": category,
    "decision": decision_made
})
sdc_csv = os.path.join(OUT_DIR, "self_driving_synth.csv")
sdc_df.to_csv(sdc_csv, index=False)

print("DATASETS_WRITTEN", hiring_csv, health_csv, sdc_csv)