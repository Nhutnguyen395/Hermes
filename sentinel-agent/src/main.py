from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from src.agent import diagnose_alert
from src.executor.kafka_actions import publish_purge_event
from src.db.database import init_db, create_incident, get_pending_incidents, get_incident, update_incident_status

app = FastAPI(title="Hermes Sentinel SRE Agent")
init_db()

AGENT_DIAGNOSES_TOTAL = Counter(
    'sentinel_diagnoses_total',
    'Total number of alerts diagnosed by the agent',
    ['risk_tier', 'action']
)

AGENT_ERRORS_TOTAl = Counter(
    'sentinel_errors_total',
    'Total number of errors encountered during agent processing'
)

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    """ Endpoint for Prometheus to scrape our custom metrics. """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

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
                diagnosis = diagnose_alert(alert)

                # Print for observability
                print("--- NEW INCIDENT DIAGNOSIS ---")
                print(f"Cause: {diagnosis.root_cause}")
                print(f"Action: {diagnosis.recommended_action}")
                print(f"Assigned Tier: {diagnosis.risk_tier.upper()}")

                AGENT_DIAGNOSES_TOTAL.labels(
                    risk_tier=diagnosis.risk_tier,
                    action=diagnosis.recommended_action
                ).inc()

                if diagnosis.risk_tier == "auto":
                    print("[!] Auto-remediation authorized. Executing...")
                    if diagnosis.recommended_action == "purge_key" and diagnosis.target_resource != "none":
                        publish_purge_event(diagnosis.target_resource)
                else:
                    print("[-] Remediation requires human approval. Escalating...")
                    ticket_id = create_incident(
                        root_cause=diagnosis.root_cause,
                        action=diagnosis.recommended_action,
                        target=diagnosis.target_resource
                    )
                    print(f"[!] Created Incident Ticket: {ticket_id}")
                    diagnosis_dict = diagnosis.model_dump()
                    diagnosis_dict["ticket_id"] = ticket_id
                    results.append(diagnosis_dict)
                    continue

                results.append(diagnosis.model_dump())

            except Exception as e:
                print(f"[ERROR] Failed to process alert: {str(e)}")
                results.append({"error": str(e)})
    return {"status": "Success", "diagnoses": results}

@app.get("/incidents")
def view_pending_incidents():
    """ Dashboard endpoints to view all tickets awaiting approval. """
    return {"pending_tickets": get_pending_incidents()}

@app.post("/incidents/{incident_id}/approve")
def approve_ticket(incident_id: str):
    """ Human clicks "Approve" -> Executes action and resolve ticket. """
    incident = get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if incident["status"] != "PENDING":
        raise HTTPException(status_code=400, detail=f"Incident already {incident['status']}")

    # Execute action
    print(f"\n[APPROVED] Executing {incident['action']} on {incident['target']}...")
    if incident["action"] == "purge_key" and incident["target"] != "none":
        publish_purge_event(incident["target"])

    update_incident_status(incident_id, "APPROVED")
    return {"status": "success", "message": f"Incident {incident_id} approved and executed."}

@app.post("/incidents/{target_id}/deny")
def deny_incidents(incident_id: str):
    """ Human clicks 'Deny' -> Cancels the action. """
    incident = get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    update_incident_status(incident_id, "DENIED")
    print(f"\n[DENIED] Cancelled action for {incident_id}.")
    return {"status": "success", "message": f"Incident {incident_id} denied."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)