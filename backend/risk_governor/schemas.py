from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


# -----------------------------
# Inputs / API surface
# -----------------------------


class PersonaInputs(BaseModel):
    persona_id: str = Field(default="default", description="Stable persona identifier")
    risk_tolerance: Literal["low", "medium", "high"] = "medium"
    time_horizon: Literal["short", "long"] = "long"
    drawdown_sensitivity: Literal["low", "medium", "high"] = "medium"


class CaseCreateRequest(BaseModel):
    asset: str = Field(description="Asset identifier (e.g. SPY)")
    persona: PersonaInputs


class CaseCreateResponse(BaseModel):
    case_id: str
    asset: str
    persona_id: str
    created_at: datetime


class MarketEvent(BaseModel):
    asset: str
    event_type: Literal["price_jump", "vol_spike", "regime_hint", "crash_signal", "heartbeat"]
    severity: float = Field(ge=0.0, le=1.0, default=0.2)
    details: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime = Field(default_factory=datetime.utcnow)


class MarketEventIn(BaseModel):
    case_id: str
    event: MarketEvent


class OverrideRequest(BaseModel):
    case_id: str
    asset: str
    persona_id: str
    override_type: Literal["force_enable", "force_disable", "set_cap"]
    strategy_id: Literal["fire", "water", "grass"]
    value: Optional[float] = Field(default=None, description="Used for set_cap (0..1)")
    reason: str = "user_override"
    occurred_at: datetime = Field(default_factory=datetime.utcnow)


# -----------------------------
# Memory citations (audit)
# -----------------------------


class MemoryCitation(BaseModel):
    kind: Literal["kv", "vector"]
    key_or_id: str
    note: str = ""


# -----------------------------
# Reasoner outputs (typed)
# -----------------------------


MarketRegimeLabel = Literal["trend", "range", "high_vol", "crash_risk"]


class MarketRegimeClassifierOut(BaseModel):
    regime: MarketRegimeLabel
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: dict[str, float] = Field(
        default_factory=dict, description="Quant evidence used (vol, momentum, drawdown, etc.)"
    )


class PersonaRiskPolicyOut(BaseModel):
    persona_id: str
    max_dd: float = Field(ge=0.0, le=1.0, description="Max tolerated drawdown (0..1)")
    max_vol: float = Field(ge=0.0, le=2.0, description="Max tolerated annualized vol")
    horizon: Literal["short", "long"]
    panic_likelihood: float = Field(ge=0.0, le=1.0)
    citations: list[MemoryCitation] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


StopLossPolicyType = Literal["none", "fixed_pct", "trailing_pct"]


class StopLossPolicy(BaseModel):
    type: StopLossPolicyType = "none"
    pct: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Stop loss percent (0..1)")


class StrategyConstraints(BaseModel):
    position_cap_pct: float = Field(ge=0.0, le=1.0)
    max_trade_freq_per_day: int = Field(ge=0, le=100)
    stop_loss_policy: StopLossPolicy = Field(default_factory=StopLossPolicy)


StrategyStatus = Literal["ENABLED", "DISABLED"]


class StrategyDecision(BaseModel):
    strategy_id: Literal["fire", "water", "grass"]
    status: StrategyStatus
    constraints: StrategyConstraints
    rationale: str
    confidence: float = Field(ge=0.0, le=1.0)
    citations: list[MemoryCitation] = Field(default_factory=list)


class StrategyViabilityDeciderOut(BaseModel):
    asset: str
    regime: MarketRegimeLabel
    decisions: list[StrategyDecision]
    confidence: float = Field(ge=0.0, le=1.0)


class EscalationDeciderOut(BaseModel):
    escalate: bool
    reason: str
    confidence: float = Field(ge=0.0, le=1.0)
    notify_channels: list[Literal["human", "pager", "email"]] = Field(default_factory=list)


class ExecutionGuard(BaseModel):
    """
    Object consumed by downstream execution/trading service.
    This is the product: a runtime governance contract, not a recommendation.
    """

    asset: str
    as_of: datetime = Field(default_factory=datetime.utcnow)
    strategies: dict[str, dict[str, Any]] = Field(
        description="Per-strategy guardrails: status + constraints"
    )
    escalations: list[dict[str, Any]] = Field(default_factory=list)


class RunDecision(BaseModel):
    case_id: str
    asset: str
    guard: ExecutionGuard
    regime: MarketRegimeClassifierOut
    persona_policy: PersonaRiskPolicyOut
    viability: StrategyViabilityDeciderOut
    escalation: EscalationDeciderOut
    audit_id: str


class AuditReport(BaseModel):
    case_id: str
    asset: str
    created_at: datetime
    inputs: dict[str, Any]
    memory_reads: list[dict[str, Any]]
    memory_writes: list[dict[str, Any]]
    reasoner_outputs: list[dict[str, Any]]
    selected_actions: list[dict[str, Any]]
    citations: list[MemoryCitation]

