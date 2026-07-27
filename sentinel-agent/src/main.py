from dotenv import load_dotenv

load_dotenv()

from src.agent import diagnosis_alert
from fastapi import FastAPI, Request

app = FastAPI(title="Hermes Sentinel SRE Agent")

@app.post("/webhook")
async def alertmanager_webhook(request: Request):
    payload = await request.json()

    results = []
    for alert in payload.get("alerts", []):
        if alert.get("status") == "firing":
            # Ask for a diagnose
            diagnosis = diagnosis_alert(alert)

            # Print for observability
            print("--- NEW INCIDENT DIAGNOSIS ---")
            print(f"Cause: {diagnosis.root_cause}")
            print(f"Action: {diagnosis.recommended_action}")
            print(f"Assigned Tier: {diagnosis.risk_tier.upper()}")

            results.append(diagnosis.model_dump())
    return {"status": "Success", "diagnoses": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)