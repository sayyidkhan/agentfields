from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from .memory import SqliteMemory
from .schemas import (
    EscalationDeciderOut,
    MarketRegimeClassifierOut,
    MarketRegimeLabel,
    MemoryCitation,
    PersonaInputs,
    PersonaRiskPolicyOut,
    StrategyConstraints,
    StrategyDecision,
    StrategyViabilityDeciderOut,
)
from .runtime import AgentFieldLiteApp


ALLOWED_STRATEGIES: tuple[str, ...] = ("fire", "water", "grass")
ALLOWED_ACTIONS: tuple[str, ...] = ("enable", "disable", "cap_only")
AUTO_DISABLE_MIN_CONFIDENCE = 0.70


class RiskGovernorStepOut(BaseModel):
    finalize: bool = False
    next_reasoners: list[str] = Field(default_factory=list)
    note: str = ""


def register(app: AgentFieldLiteApp) -> None:
    @app.reasoner(tags=["coordination"])
    def risk_governor(
        *,
        have_regime: bool,
        have_persona_policy: bool,
        have_viability: bool,
        have_escalation: bool,
        last_confidence: float = 0.0,
    ) -> dict[str, Any]:
        """
        Coordinator reasoner: decides which specialist reasoners to call next.
        No DAG: selection is based on evidence gaps + uncertainty.
        """
        next_calls: list[str] = []

        if not have_regime:
            next_calls.append("market_regime_classifier")
        if not have_persona_policy:
            next_calls.append("persona_risk_policy")

        # Viability depends on both regime + persona policy
        if have_regime and have_persona_policy and not have_viability:
            next_calls.append("strategy_viability_decider")

        # Escalation depends on viability (and confidence)
        if have_viability and (not have_escalation or last_confidence < AUTO_DISABLE_MIN_CONFIDENCE):
            next_calls.append("escalation_decider")

        finalize = have_regime and have_persona_policy and have_viability and have_escalation
        note = "final" if finalize else "collect evidence / reduce uncertainty"

        out = RiskGovernorStepOut(finalize=finalize, next_reasoners=next_calls, note=note)
        return out.model_dump()

    @app.reasoner(tags=["market"])
    def market_regime_classifier(
        *,
        indicators: dict[str, float],
        event_type: str,
        event_severity: float,
    ) -> dict[str, Any]:
        vol = float(indicators.get("volatility", 0.0))
        dd = float(indicators.get("max_drawdown", 0.0))
        mom = float(indicators.get("momentum_20d", 0.0))
        slope = float(indicators.get("trend_slope", 0.0))

        regime: MarketRegimeLabel
        if event_type == "crash_signal" or dd <= -0.18 or (event_type == "price_jump" and event_severity > 0.75 and mom < -0.04):
            regime = "crash_risk"
        elif event_type == "vol_spike" or vol >= 0.30:
            regime = "high_vol"
        elif abs(mom) >= 0.04 and abs(slope) >= 0.0008:
            regime = "trend"
        else:
            regime = "range"

        # confidence: strength of rule triggers
        conf = 0.55
        if regime == "crash_risk":
            conf = min(0.95, 0.70 + min(0.25, abs(dd) / 0.25) + 0.10 * float(event_severity))
        elif regime == "high_vol":
            conf = min(0.92, 0.62 + min(0.25, vol / 0.45) + 0.08 * float(event_severity))
        elif regime == "trend":
            conf = min(0.90, 0.60 + min(0.20, abs(mom) / 0.10) + min(0.10, abs(slope) / 0.01))
        else:
            conf = 0.70 if vol < 0.22 and abs(mom) < 0.03 else 0.62

        out = MarketRegimeClassifierOut(
            regime=regime,
            confidence=round(float(conf), 4),
            evidence={
                "volatility": round(vol, 4),
                "max_drawdown": round(dd, 4),
                "momentum_20d": round(mom, 4),
                "trend_slope": round(slope, 6),
                "event_severity": round(float(event_severity), 4),
            },
        )
        return out.model_dump()

    @app.reasoner(tags=["persona", "memory"])
    def persona_risk_policy(
        *,
        persona: dict[str, Any],
        memory: SqliteMemory,
    ) -> dict[str, Any]:
        p = PersonaInputs(**persona)
        citations: list[MemoryCitation] = []

        scope = f"persona:{p.persona_id}"
        behavior_key = "behavior"
        behavior = memory.get(scope, behavior_key) or {}
        citations.append(
            MemoryCitation(
                kind="kv",
                key_or_id=f"{scope}/{behavior_key}",
                note="persona behavior",
            )
        )

        # Base thresholds from persona inputs (deterministic mapping)
        risk = p.risk_tolerance
        dd_sens = p.drawdown_sensitivity
        horizon = p.time_horizon

        base_max_dd = {"low": 0.10, "medium": 0.18, "high": 0.28}[risk]
        base_max_vol = {"low": 0.18, "medium": 0.28, "high": 0.40}[risk]
        if horizon == "short":
            base_max_dd *= 0.85
            base_max_vol *= 0.90
        if dd_sens == "high":
            base_max_dd *= 0.80
        elif dd_sens == "low":
            base_max_dd *= 1.10

        # Panic likelihood inferred from behavior memory
        panic_events = int(behavior.get("panic_events", 0))
        overrides = int(behavior.get("overrides", 0))
        last_panic_dd = float(behavior.get("last_panic_drawdown", 0.0))
        panic = min(1.0, 0.10 + 0.18 * panic_events + 0.08 * overrides + 0.60 * max(0.0, -last_panic_dd))
        panic = float(round(panic, 4))

        # De-risk thresholds if panic likely
        max_dd = float(round(base_max_dd * (1.0 - 0.25 * panic), 4))
        max_vol = float(round(base_max_vol * (1.0 - 0.20 * panic), 4))

        conf = 0.78 if behavior else 0.70
        conf = float(round(min(0.90, conf + 0.05 * (1.0 - panic)), 4))

        out = PersonaRiskPolicyOut(
            persona_id=p.persona_id,
            max_dd=max_dd,
            max_vol=max_vol,
            horizon=horizon,
            panic_likelihood=panic,
            citations=citations,
            confidence=conf,
        )
        return out.model_dump()

    @app.reasoner(tags=["strategy", "memory"])
    def strategy_viability_decider(
        *,
        asset: str,
        regime: dict[str, Any],
        persona_policy: dict[str, Any],
        indicators: dict[str, float],
        memory: SqliteMemory,
    ) -> dict[str, Any]:
        reg = MarketRegimeClassifierOut(**regime)
        pol = PersonaRiskPolicyOut(**persona_policy)

        # Vector memory: similar incidents for this asset (regime shifts, drawdowns, overrides)
        query = (
            f"asset={asset} regime={reg.regime} vol={indicators.get('volatility')} "
            f"dd={indicators.get('max_drawdown')} panic={pol.panic_likelihood}"
        )
        vec_scope = f"asset:{asset}"
        similar = memory.search(vec_scope, query, top_k=3)
        citations: list[MemoryCitation] = []
        for s in similar:
            citations.append(
                MemoryCitation(kind="vector", key_or_id=s["vector_id"], note=f"similarity={s['score']:.3f}")
            )

        vol = float(indicators.get("volatility", 0.0))
        dd = float(indicators.get("max_drawdown", 0.0))

        def c(position_cap: float, freq: int, sl_type: str, sl_pct: Optional[float]) -> StrategyConstraints:
            return StrategyConstraints(
                position_cap_pct=position_cap,
                max_trade_freq_per_day=freq,
                stop_loss_policy={"type": sl_type, "pct": sl_pct},
            )

        decisions: list[StrategyDecision] = []

        # Base constraints by regime (governance, not alpha selection)
        if reg.regime == "crash_risk":
            fire = ("DISABLED", c(0.05, 0, "fixed_pct", 0.05), "Crash risk: momentum is fragile.")
            water = ("ENABLED", c(0.70, 2, "fixed_pct", 0.10), "Crash risk: preserve capital, trade rarely.")
            grass = ("ENABLED", c(0.30, 1, "fixed_pct", 0.08), "Crash risk: adaptive allowed with tight brakes.")
        elif reg.regime == "high_vol":
            fire = ("ENABLED", c(0.15, 1, "fixed_pct", 0.08), "High vol: allow fire only with tight cap.")
            water = ("ENABLED", c(0.55, 2, "fixed_pct", 0.10), "High vol: conservative dominates.")
            grass = ("ENABLED", c(0.35, 2, "fixed_pct", 0.09), "High vol: adaptive allowed, capped.")
        elif reg.regime == "trend":
            fire = ("ENABLED", c(0.45, 4, "trailing_pct", 0.12), "Trend: allow momentum with guardrails.")
            water = ("ENABLED", c(0.35, 2, "none", None), "Trend: conservative allowed but capped.")
            grass = ("ENABLED", c(0.40, 3, "trailing_pct", 0.12), "Trend: adaptive allowed.")
        else:  # range
            fire = ("ENABLED", c(0.25, 2, "fixed_pct", 0.10), "Range: momentum risk; keep smaller cap.")
            water = ("ENABLED", c(0.55, 3, "fixed_pct", 0.10), "Range: mean reversion fits.")
            grass = ("ENABLED", c(0.35, 2, "fixed_pct", 0.10), "Range: adaptive allowed.")

        # Persona policy overrides: if risk limits exceeded, tighten caps.
        persona_tighten = 1.0
        if vol > pol.max_vol:
            persona_tighten *= 0.75
        if abs(dd) > pol.max_dd:
            persona_tighten *= 0.70
        persona_tighten *= (1.0 - 0.20 * pol.panic_likelihood)
        persona_tighten = max(0.10, min(1.0, persona_tighten))

        def apply_tighten(decision_tuple):
            status, con, rationale = decision_tuple
            con2 = con.model_copy(deep=True)
            con2.position_cap_pct = float(round(con2.position_cap_pct * persona_tighten, 4))
            return status, con2, rationale

        fire = apply_tighten(fire)
        water = apply_tighten(water)
        grass = apply_tighten(grass)

        # Memory influence: if similar incidents show user panics, de-risk earlier
        similar_panic = any(s["score"] >= 0.35 and "override" in (s["text"] or "").lower() for s in similar)
        if similar_panic and pol.panic_likelihood >= 0.35:
            # deterministic adjustment: cut aggressive caps by 20%
            status, con, rat = fire
            con.position_cap_pct = float(round(con.position_cap_pct * 0.80, 4))
            fire = (status, con, rat + " Memory: prior panic/override -> earlier de-risk.")

        # Confidence model (bounded, deterministic)
        conf = min(reg.confidence, pol.confidence)
        # penalize if indicators breach persona limits (more uncertain / escalatory)
        if vol > pol.max_vol * 1.15 or abs(dd) > pol.max_dd * 1.15:
            conf *= 0.85
        conf = float(round(max(0.50, min(0.92, conf)), 4))

        def mk(strategy_id: Literal["fire", "water", "grass"], tup):
            status, con, rationale = tup
            local_conf = conf
            # guided autonomy: low confidence => never auto-disable; cap-only instead
            if status == "DISABLED" and local_conf < AUTO_DISABLE_MIN_CONFIDENCE:
                status = "ENABLED"
                con.position_cap_pct = min(con.position_cap_pct, 0.05)
                con.max_trade_freq_per_day = 0
                rationale = rationale + " Low confidence: no auto-disable; cap-only + escalate."
                local_conf = float(round(min(local_conf, 0.69), 4))
            return StrategyDecision(
                strategy_id=strategy_id,
                status=status,  # type: ignore[arg-type]
                constraints=con,
                rationale=rationale,
                confidence=local_conf,
                citations=citations,
            )

        decisions.append(mk("fire", fire))
        decisions.append(mk("water", water))
        decisions.append(mk("grass", grass))

        out = StrategyViabilityDeciderOut(
            asset=asset,
            regime=reg.regime,
            decisions=decisions,
            confidence=conf,
        )
        return out.model_dump()

    @app.reasoner(tags=["safety"])
    def escalation_decider(
        *,
        regime: dict[str, Any],
        persona_policy: dict[str, Any],
        viability: dict[str, Any],
    ) -> dict[str, Any]:
        reg = MarketRegimeClassifierOut(**regime)
        pol = PersonaRiskPolicyOut(**persona_policy)
        v = StrategyViabilityDeciderOut(**viability)

        # Escalate on:
        # - uncertainty: confidence below 0.70
        # - risk beyond persona bounds (implied by crash_risk)
        # - any strategy decision that is "cap-only due to low confidence" (signals ambiguity)
        escalate = False
        reasons: list[str] = []
        if v.confidence < AUTO_DISABLE_MIN_CONFIDENCE:
            escalate = True
            reasons.append("low_confidence")
        if reg.regime == "crash_risk":
            escalate = True
            reasons.append("crash_risk_regime")
        if pol.panic_likelihood >= 0.60:
            escalate = True
            reasons.append("high_panic_likelihood")

        # detect cap-only fallback
        for d in v.decisions:
            if d.strategy_id == "fire" and d.status == "ENABLED" and d.constraints.max_trade_freq_per_day == 0 and d.confidence < AUTO_DISABLE_MIN_CONFIDENCE:
                escalate = True
                reasons.append("cap_only_fallback")
                break

        reason = ", ".join(sorted(set(reasons))) if reasons else "within_bounds"
        conf = float(round(min(0.95, max(0.60, v.confidence)), 4))
        out = EscalationDeciderOut(
            escalate=bool(escalate),
            reason=reason,
            confidence=conf,
            notify_channels=(["human"] if escalate else []),
        )
        return out.model_dump()

