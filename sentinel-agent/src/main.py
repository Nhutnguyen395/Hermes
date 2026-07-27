from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request, HTTPException
from src.agent import diagnosis_alert
from src.executor.kafka_actions import publish_purge_event

app = FastAPI(title="Hermes Sentinel SRE Agent")

@app.post("/webhook")
async def alertmanager_webhook(request: Request):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    results = []
    for alert in payload.get("alerts", []):
        if alert.get("status") == "firing":
            try:
                # Ask for a diagnose
                diagnosis = diagnosis_alert(alert)

                # Print for observability
                print("--- NEW INCIDENT DIAGNOSIS ---")
                print(f"Cause: {diagnosis.root_cause}")
                print(f"Action: {diagnosis.recommended_action}")
                print(f"Assigned Tier: {diagnosis.risk_tier.upper()}")

                if diagnosis.risk_tier == "auto":
                    print("[!] Auto-remediation authorized. Executing...")

                    if diagnosis.recommended_action == "purge_key" and diagnosis.target_resource:
                        publish_purge_event(diagnosis.target_resource)
                    elif diagnosis.recommended_action == "scale_replica":
                        print(f"[!] Pending k8s scaling for {diagnosis.target_resource}")

                else:
                    print("[-] Remediation requires human approval. Escalating...")

                results.append(diagnosis.model_dump())
            except Exception as e:
                print(f"[ERROR] Failed to process alert: {str(e)}")
                results.append({"error": str(e)})
    return {"status": "Success", "diagnoses": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)