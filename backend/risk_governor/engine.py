from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from .db import (
    get_case,
    get_latest_decision,
    insert_event,
)
from .memory import SqliteMemory
from .runtime import AgentFieldLiteApp, ExecutionBudget
from .schemas import (
    AuditReport,
    ExecutionGuard,
    MarketEvent,
    MarketRegimeClassifierOut,
    EscalationDeciderOut,
    PersonaRiskPolicyOut,
    RunDecision,
    StrategyViabilityDeciderOut,
)


def _json_loads(s: str) -> Any:
    return json.loads(s)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


@dataclass
class RiskGovernorEngine:
    app: AgentFieldLiteApp
    db_path: str

    def _connect(self):
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    async def process_market_event(
        self,
        *,
        case_id: str,
        event: MarketEvent,
        budget: Optional[ExecutionBudget] = None,
    ) -> RunDecision:
        budget = budget or ExecutionBudget()

        with self._connect() as conn:
            case = get_case(conn, case_id)
            if case is None:
                raise KeyError(f"case_id not found: {case_id}")

            asset = str(case["asset"])
            inputs = _json_loads(case["inputs_json"])
            persona = inputs.get("persona", {})

            memory = SqliteMemory(conn)

            audit_id = f"audit_{uuid.uuid4().hex}"
            decision_id = f"dec_{uuid.uuid4().hex}"
            event_id = f"evt_{uuid.uuid4().hex}"

            insert_event(
                conn,
                event_id=event_id,
                case_id=case_id,
                asset=asset,
                occurred_at=_iso(event.occurred_at),
                event=event.model_dump(),
            )

            memory_reads: list[dict[str, Any]] = []
            memory_writes: list[dict[str, Any]] = []
            reasoner_outputs: list[dict[str, Any]] = []
            selected_actions: list[dict[str, Any]] = []
            citations: list[dict[str, Any]] = []

            # -----------------------------
            # Deterministic skills: fetch data -> indicators
            # -----------------------------
            prices_blob = await self.app.call(
                "fetch_market_data", budget=budget, asset=asset, window=252
            )
            indicators = await self.app.call(
                "compute_indicators", budget=budget, prices=prices_blob["prices"]
            )

            # -----------------------------
            # Guided autonomy loop (bounded, non-DAG)
            # -----------------------------
            regime: Optional[dict[str, Any]] = None
            persona_policy: Optional[dict[str, Any]] = None
            viability: Optional[dict[str, Any]] = None
            escalation: Optional[dict[str, Any]] = None

            while True:
                budget.bump_step()

                last_conf = float(viability.get("confidence", 0.0)) if viability else 0.0
                step = await self.app.call(
                    "risk_governor",
                    budget=budget,
                    have_regime=regime is not None,
                    have_persona_policy=persona_policy is not None,
                    have_viability=viability is not None,
                    have_escalation=escalation is not None,
                    last_confidence=last_conf,
                )
                reasoner_outputs.append({"name": "risk_governor", "output": step})

                if step.get("finalize"):
                    break

                for rname in step.get("next_reasoners", []):
                    if rname == "market_regime_classifier" and regime is None:
                        regime = await self.app.call(
                            rname,
                            budget=budget,
                            indicators=indicators,
                            event_type=event.event_type,
                            event_severity=event.severity,
                        )
                        reasoner_outputs.append({"name": rname, "output": regime})
                    elif rname == "persona_risk_policy" and persona_policy is None:
                        # memory read (tracked)
                        scope = f"persona:{persona.get('persona_id', 'default')}"
                        behavior = memory.get(scope, "behavior")
                        memory_reads.append(
                            {"kind": "kv", "scope": scope, "key": "behavior", "hit": behavior is not None}
                        )
                        persona_policy = await self.app.call(
                            rname,
                            budget=budget,
                            persona=persona,
                            memory=memory,
                        )
                        reasoner_outputs.append({"name": rname, "output": persona_policy})
                        citations.extend(persona_policy.get("citations", []))
                    elif rname == "strategy_viability_decider" and viability is None:
                        viability = await self.app.call(
                            rname,
                            budget=budget,
                            asset=asset,
                            regime=regime or {},
                            persona_policy=persona_policy or {},
                            indicators=indicators,
                            memory=memory,
                        )
                        reasoner_outputs.append({"name": rname, "output": viability})
                        # citations on each decision
                        for d in viability.get("decisions", []):
                            citations.extend(d.get("citations", []))
                    elif rname == "escalation_decider" and escalation is None:
                        escalation = await self.app.call(
                            rname,
                            budget=budget,
                            regime=regime or {},
                            persona_policy=persona_policy or {},
                            viability=viability or {},
                        )
                        reasoner_outputs.append({"name": rname, "output": escalation})

                if budget.steps_used >= budget.max_steps:
                    break

            if regime is None or persona_policy is None or viability is None or escalation is None:
                raise RuntimeError("RiskGovernor loop terminated without required outputs.")

            # -----------------------------
            # Deterministic action execution: generate execution guard
            # -----------------------------
            guard_strategies: dict[str, dict[str, Any]] = {}
            v = StrategyViabilityDeciderOut(**viability)
            allowed_strategies = {"fire", "water", "grass"}
            for d in v.decisions:
                if d.strategy_id not in allowed_strategies:
                    raise RuntimeError(f"strategy not allowlisted: {d.strategy_id}")
                exec_guard = await self.app.call(
                    "apply_policy_constraints",
                    budget=budget,
                    strategy_id=d.strategy_id,
                    constraints=d.constraints.model_dump(),
                    status=d.status,
                )
                guard_strategies[d.strategy_id] = exec_guard
                if d.status == "DISABLED":
                    action = "disable"
                elif d.constraints.position_cap_pct < 1.0:
                    action = "cap_only"
                else:
                    action = "enable"
                selected_actions.append(
                    {
                        "action": action,
                        "strategy_id": d.strategy_id,
                        "status": d.status,
                        "constraints": d.constraints.model_dump(),
                        "confidence": d.confidence,
                    }
                )

            guard = ExecutionGuard(
                asset=asset,
                as_of=datetime.utcnow(),
                strategies=guard_strategies,
                escalations=(
                    [{"reason": escalation.get("reason"), "channels": escalation.get("notify_channels", [])}]
                    if escalation.get("escalate")
                    else []
                ),
            )

            # optional stubs
            if escalation.get("escalate"):
                await self.app.call(
                    "notify",
                    budget=budget,
                    payload={"case_id": case_id, "asset": asset, "reason": escalation.get("reason")},
                )
                await self.app.call(
                    "emit_risk_event",
                    budget=budget,
                    payload={"case_id": case_id, "asset": asset, "event_type": event.event_type, "severity": event.severity},
                )

            # -----------------------------
            # Memory writes: latest decision + incident vectors
            # -----------------------------
            memory.set(f"asset:{asset}", "latest_decision", guard.model_dump())
            memory_writes.append(
                {"kind": "kv", "scope": f"asset:{asset}", "key": "latest_decision"}
            )

            # add vector memory on regime shifts / high severity
            vec_scope = f"asset:{asset}"
            incident_text = (
                f"market_event override? asset={asset} event={event.event_type} severity={event.severity} "
                f"regime={regime.get('regime')} vol={indicators.get('volatility')} dd={indicators.get('max_drawdown')}"
            )
            vec_id = memory.add_vector(
                vec_scope,
                incident_text,
                metadata={
                    "case_id": case_id,
                    "event_type": event.event_type,
                    "severity": event.severity,
                    "regime": regime.get("regime"),
                },
            )
            memory_writes.append({"kind": "vector", "scope": vec_scope, "vector_id": vec_id})
            citations.append({"kind": "vector", "key_or_id": vec_id, "note": "incident recorded"})

            # -----------------------------
            # Persist audit + decision (Skills: persistence)
            # -----------------------------
            report = AuditReport(
                case_id=case_id,
                asset=asset,
                created_at=datetime.utcnow(),
                inputs={"case": inputs, "event": event.model_dump(), "indicators": indicators},
                memory_reads=memory_reads,
                memory_writes=memory_writes,
                reasoner_outputs=reasoner_outputs,
                selected_actions=selected_actions,
                citations=[c for c in citations],
            ).model_dump()

            await self.app.call(
                "persist_audit",
                budget=budget,
                conn=conn,
                audit_id=audit_id,
                case_id=case_id,
                asset=asset,
                report=report,
            )

            await self.app.call(
                "persist_decision",
                budget=budget,
                conn=conn,
                decision_id=decision_id,
                case_id=case_id,
                asset=asset,
                guard=guard.model_dump(),
                audit_id=audit_id,
            )

            # -----------------------------
            # Output bundle (typed)
            # -----------------------------
            regime_out = MarketRegimeClassifierOut(**regime)
            persona_out = PersonaRiskPolicyOut(**persona_policy)
            escalation_out = EscalationDeciderOut(**escalation)
            return RunDecision(
                case_id=case_id,
                asset=asset,
                guard=guard,
                regime=regime_out,
                persona_policy=persona_out,
                viability=v,
                escalation=escalation_out,
                audit_id=audit_id,
            )

    def get_latest_guard(self, asset: str) -> Optional[dict[str, Any]]:
        with self._connect() as conn:
            row = get_latest_decision(conn, asset)
            if row is None:
                return None
            return _json_loads(row["guard_json"])

