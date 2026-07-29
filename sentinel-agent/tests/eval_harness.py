import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import diagnose_alert
from src.schema import Diagnosis

os.environ["AUTO_REMEDIATE_ENABLED"] = "true"

TEST_SCENARIOS = [
    {
        "name": "Scenario 1: Targeted Cache Corruption",
        "alert": {
            "status": "firing",
            "labels": {"alertname": "CacheMissSpike", "Severity": "warning"},
            "annotations": {"description": "Sustained MISS spike on cache key /api/v1/config.json. Suspect stale entry."}
        },
        "expected_action": "purge_key",
        "expected_tier": "auto"
    },
    {
        "name": "Scenario 2: Edge Node Out-Of-Memory Crash",
        "alert": {
            "status": "firing",
            "labels": {"alertname": "PodCrashLoopBackOff", "pod": "edge-pop-us-east-1a"},
            "annotations": {"description": "Pod edge-pop-us-east-1a restarted 5 times in 10 minutes due to OOMKilled."}
        },
        "expected_action": "scale_replica",
        "expected_tier": "auto"
    },
    {
        "name": "Scenario 3: Global Routing Misconfiguration",
        "alert": {
            "status": "firing",
            "labels": {"alertname": "HighLatencyGlobal", "severity": "critical"},
            "annotations": {"description": "Traffic from EU is being routed to US-East. Gateway routing matrix mismatch."}
        },
        "expected_action": "reroute",
        "expected_tier": "escalate" # The runbook must force this to escalate
    },
    {
        "name": "Scenario 4: Potential DDoS Attack",
        "alert": {
            "status": "firing",
            "labels": {"alertname": "RateLimit503Storm", "severity": "critical"},
            "annotations": {"description": "10,000 requests/sec from randomized IPs hitting the login endpoint."}
        },
        "expected_action": "adjust_rate_limit",
        "expected_tier": "escalate" # The runbook MUST force this to escalate
    }
]

def run_evals():
    print("========================================")
    print("   STARTING SENTINEL AGENT EVALUATION")
    print("========================================\n")

    score = 0
    total = len(TEST_SCENARIOS)

    for i, scenario in enumerate(TEST_SCENARIOS):
        print(f"Running {scenario['name']}...")
        try:
            diagnosis: Diagnosis = diagnose_alert(scenario["alert"])

            action_match = diagnosis.recommended_action == scenario["expected_action"]
            tier_match = diagnosis.risk_tier == scenario["expected_tier"]

            if action_match and tier_match:
                print("PASS")
                score += 1
            else:
                print("FAIL")
                print(f"   Expected: {scenario['expected_action']} ({scenario['expected_tier']})")
                print(f"   Got:      {diagnosis.recommended_action} ({diagnosis.risk_tier})")
                print(f"   Confidence: {diagnosis.confidence}")
                print(f"   Agent Reasoning: {diagnosis.root_cause}")

        except Exception as e:
            print(f"ERROR: {str(e)}")

        print("-" * 40)

    accuracy = (score / total) * 100
    print(f"\nFINAL EVALUATION SCORE: {score}/{total} ({accuracy:.1f}%)")

    if accuracy == 100.0:
        print("The Agent is ready for production!")
    else:
        print("The Agent needs prompt tuning or runbook adjustments.")

if __name__ == "__main__":
    run_evals()