from pydantic import BaseModel, Field
from typing_extensions import Literal, List

class Diagnosis(BaseModel):
    root_cause: str = Field(description="A 1-2 sentence explanation of the failure.")
    confidence: float = Field(description="Confidence score from 0.0 to 1.0")
    affected_component: Literal["edge_pop", "origin", "gateway", "kafka", "auth"]
    recommended_action: Literal["purge_key", "scale_replica", "adjust_rate_limit", "reroute", "rollback_auth", "purge_all", "no_action"]
    risk_tier: Literal["auto", "escalate"]
    evidence: List[str] = Field(description="List of metrics or log signals that led to this diagnosis.")