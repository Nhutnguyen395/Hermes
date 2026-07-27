# Hermes Sentinel — Automated Incident Response Runbook

## Overview
This runbook defines the risk-tiered autonomy model for the Hermes Sentinel Agent.
The Sentinel Agent utilizes an LLM (Gemini) to diagnose root causes based on Prometheus telemetry. However, **the LLM is never trusted to determine its own execution permissions.**

Every diagnosis maps to a hardcoded Risk Tier. If the LLM suggests an action or tier that conflicts with this table, the system defaults to the highest restriction (Escalate).

## Risk Tier Definitions
* **Auto :** Low-risk, idempotent, and narrowly scoped actions. The agent executes these immediately via Kubernetes API or Kafka events and logs the action.
* **Escalate :** High-risk, broad blast radius, or security-sensitive actions. The agent stages the action, pages a human via Slack, and waits for explicit approval.

## Failure Scenarios & Allowed Actions

| Failure Signal (Prometheus/Log) | Root Cause Diagnosis | Allowed Action | Risk Tier | Justification |
| :--- | :--- | :--- | :--- | :--- |
| **Sustained MISS spike on specific cache key** | Stale/Corrupt Cache Entry | `purge_key` | **Auto** | Targeted MD5 purge is scoped to a single item. Handled via existing Kafka invalidation pipeline. Safe to repeat. |
| **Single edge PoP replica unhealthy (Crash/OOM)** | Pod Crash / OOM | `scale_replica` | **Auto** | Scaling up `+1` replica is non-destructive and handles temporary capacity drops. |
| **Rate-limit 503 storm from randomized IPs** | Suspected DDoS or Misconfigured Client | `adjust_rate_limit` | **Escalate** | Changing token-bucket thresholds globally can drop legitimate traffic. Requires human context. |
| **Gateway API routing misdirecting a region** | Config Drift / Bad Geo-routing | `reroute` | **Escalate** | Touching BGP/Geo-routing logic can cause cascading regional failures. Never auto-touch routing. |
| **Repeated JWT validation failures** | Auth0/JWKS Issue or Attack | `rollback_auth` | **Escalate** | Security domain. Modifying auth logic or rolling back identity services requires human oversight. |
| **Global Cache Hit Rate drops < 10%** | Catastrophic Cache Wipe | `purge_all` | **Escalate** | High blast radius. A full purge forces all traffic to the Origin, potentially causing an Origin OOM crash. |

## Safety Overrides
1. **The Fallback Rule:** If the LLM returns an action not explicitly listed in the table above, the tier defaults to **Escalate**.
2. **The Confidence Threshold:** Even if an action is tiered as **Auto**, if the LLM's diagnostic confidence score is `< 0.85`, it is automatically downgraded to **Escalate**.
3. **The Kill Switch:** A Kubernetes ConfigMap flag (`AUTO_REMEDIATE_ENABLED=false`) will completely bypass the auto-execution pathway for emergency manual overrides.