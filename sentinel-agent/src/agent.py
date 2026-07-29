import os
from google import genai
from google.genai import types
from src.schema import Diagnosis
from src.risk_classifier import enforce_safety_guardrails

# Initialize the modern google-genai client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def diagnose_alert(alert_payload: dict) -> Diagnosis:
    prompt = f"""
    You are an expert SRE Agent for the Hermes CDN.
    Analyze the following Prometheus alert payload and diagnose the root cause.
    
    CRITICAL RUNBOOK RULES (Follow these mappings strictly):
    1. If the alert is about a Cache Miss Spike or Stale Entry -> Action MUST be 'purge_key'.
    2. If the alert is about a Pod Crash, OOMKilled, or PodCrashLoopBackOff -> Action MUST be 'scale_replica'.
    3. If the alert is about Gateway Routing Mismatch or high global latency -> Action MUST be 'reroute'.
    4. If the alert is about a DDoS, 503 Storm, or massive request spikes -> Action MUST be 'adjust_rate_limit'.
    
    Be highly confident (0.9 or 1.0) if the alert is perfectly matches these rules.
    Do not output markdown, only the structured JSON requested.
    
    Alert Data:
    {alert_payload}
    """

    response = client.models.generate_content(
        model='gemini-3.5-flash-lite',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema=Diagnosis,
            temperature=0.1
        ),
    )

    llm_diagnosis = response.parsed
    auto_enabled = os.getenv("AUTO_REMEDIATE_ENABLED", "false").lower() == "true"
    final_diagnosis = enforce_safety_guardrails(llm_diagnosis, auto_enabled)
    return final_diagnosis