from src.schema import Diagnosis

# The absolute ground truth mapped from the Runbook
ALLOWED_AUTO_ACTIONS = ["purge_key", "scale_replica"]

def enforce_safety_guardrails(diagnosis: Diagnosis, auto_enabled: bool = True) -> Diagnosis:
    """
    Overrides the LLM's risk tier if it violates the hardcoded runbook rules
    """

    # Override 1: The kill switch
    if not auto_enabled:
        diagnosis.risk_tier = "escalate"
        return diagnosis

    # Override 2: The confidence threshold
    if diagnosis.confidence < 0.85:
        diagnosis.risk_tier = "escalate"

    # Override 3: The Fallback Rule (Action not allowed for auto)
    if diagnosis.recommended_action not in ALLOWED_AUTO_ACTIONS:
        diagnosis.risk_tier = "escalate"

    return diagnosis