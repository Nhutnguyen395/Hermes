import urllib.request
import json
import time

WEBHOOK_URL = "http://localhost:8080/webhook"

# The 5 scenarios from our Runbook
SCENARIOS = [
    {
        "name": "Scenario 1: Targeted Cache Corruption (AUTO)",
        "payload": {
            "alerts": [{
                "status": "firing",
                "labels": {"alertname": "CacheMissSpike", "severity": "warning"},
                "annotation": {"description": "Sustained MISS spike on cache key /assets/video.mp4. Suspect statle entry"}
            }]
        }
    },
    {
        "name": "Scenario 2: Edge Node OOM Crash (AUTO)",
        "payload": {
            "alerts": [{
                "status": "firing",
                "labels": {"alertname": "PodCrashLoopBackOff", "pod": "edge-pop-us-east"},
                "annotations": {"description": "Pod edge-pop-us-east restarted 5 times due to OOMKilled."}
            }]
        }
    },
    {
        "name": "Scenario 3: Global Routing Misconfiguration (ESCALATE)",
        "payload": {
            "alerts": [{
                "status": "firing",
                "labels": {"alertname": "HighLatencyGlobal", "severity": "critical"},
                "annotations": {"description": "Traffic from EU is being routed to US-East. Gateway routing matrix mismatch."}
            }]
        }
    },
    {
        "name": "Scenario 4: JWT Auth Failure Spike (ESCALATE)",
        "payload": {
            "alerts": [{
                "status": "firing",
                "labels": {"alertname": "AuthFailureSpike", "severity": "critical"},
                "annotations": {"description": "Repeated JWT validation failures. Possible Auth0/JWKS issue or attack."}
            }]
        }
    },
    {
        "name": "Scenario 5: Global Cache Wipe (ESCALATE)",
        "payload": {
            "alerts": [{
                "status": "firing",
                "labels": {"alertname": "CatastrophicCacheHitDrop", "severity": "critical"},
                "annotations": {"description": "Global Cache Hit Rate dropped below 10%. Massive origin overload imminent."}
            }]
        }
    }
]

def run_simulation():
    print("===================================================")
    print("  STARTING ALERTMANAGER WEBHOOK SIMULATION SUITE")
    print("===================================================\n")

    for scenario in SCENARIOS:
        print(f"Firing {scenario['name']}...")

        req = urllib.request.Request(
            WEBHOOK_URL,
            data=json.dumps(scenario["payload"]).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    print("Webhook accepted by agent.")
                else:
                    print("Failed with status: {response.status}")
        except Exception as e:
            print(f"Connection error: e")
            print("Did you forget to port-forward the sentinel-agent-svc?")
            return

        time.sleep(3)
        print("-" * 50)
        print("\nSIMULATION COMPLETE. Check your Agent logs!")

if __name__ == "__main__":
    run_simulation()