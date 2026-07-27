import os
from google import genai
from google.genai import types
from src.schema import Diagnosis
from src.risk_classifier import enforce_safety_guardrails

# Initialize the modern google-genai client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def diagnosis_alert(alert_payload: dict) -> Diagnosis:
    prompt = f"""
    You are an expert SRE Agent for the Hermes CDN.
    Analyze the following Prometheus alert payload and diagnose the root cause.
    Do not output markdown, only the structured JSON requested.
    
    Alert Data:
    {alert_payload}
    """

    response = client.models.generate_content(
        model='gemini-3.5-flash',
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