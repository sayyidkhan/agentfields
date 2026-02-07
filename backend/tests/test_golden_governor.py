import sys
import tempfile
from pathlib import Path

import pytest


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


from risk_governor.db import SqliteDB, insert_case
from risk_governor.engine import RiskGovernorEngine
from risk_governor.memory import SqliteMemory
from risk_governor.runtime import AgentFieldLiteApp
from risk_governor.schemas import (
    CaseCreateRequest,
    MarketEvent,
    MarketRegimeClassifierOut,
    PersonaRiskPolicyOut,
    StrategyViabilityDeciderOut,
)
from risk_governor import skills as skills_mod
from risk_governor import reasoners as reasoners_mod
from risk_governor import persistence_skills as persistence_mod


def _build_engine(tmp_db_path: str) -> RiskGovernorEngine:
    SqliteDB(Path(tmp_db_path)).migrate()
    app = AgentFieldLiteApp(node_id="risk-governor")
    skills_mod.register(app)
    persistence_mod.register(app)
    reasoners_mod.register(app)
    return RiskGovernorEngine(app=app, db_path=tmp_db_path)


@pytest.mark.asyncio
async def test_reasoner_outputs_validate_and_policy_respected():
    with tempfile.TemporaryDirectory() as td:
        db_path = str(Path(td) / "rg.sqlite")
        engine = _build_engine(db_path)

        # Insert a case (bypass API)
        import sqlite3
        from datetime import datetime

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        with conn:
            insert_case(
                conn,
                case_id="case_test",
                asset="SPY",
                persona_id="p1",
                created_at=datetime.utcnow().isoformat(),
                inputs=CaseCreateRequest(
                    asset="SPY",
                    persona={"persona_id": "p1", "risk_tolerance": "medium", "time_horizon": "long", "drawdown_sensitivity": "high"},
                ).model_dump(),
            )
            # seed persona behavior memory
            mem = SqliteMemory(conn)
            mem.set("persona:p1", "behavior", {"panic_events": 1, "overrides": 0, "last_panic_drawdown": -0.12})

        # Run a crash-ish event
        decision = await engine.process_market_event(
            case_id="case_test",
            event=MarketEvent(asset="SPY", event_type="crash_signal", severity=0.8, details={}),
        )

        # Schema validation
        MarketRegimeClassifierOut(**decision.regime.model_dump() if hasattr(decision.regime, "model_dump") else decision.regime)  # type: ignore[arg-type]
        PersonaRiskPolicyOut(**decision.persona_policy.model_dump() if hasattr(decision.persona_policy, "model_dump") else decision.persona_policy)  # type: ignore[arg-type]
        StrategyViabilityDeciderOut(**decision.viability.model_dump() if hasattr(decision.viability, "model_dump") else decision.viability)  # type: ignore[arg-type]

        guard = decision.guard.model_dump()
        assert "fire" in guard["strategies"]
        assert "water" in guard["strategies"]

        # In crash risk, fire should be disabled OR tightly capped with trade freq 0
        fire = guard["strategies"]["fire"]
        if fire["status"] == "DISABLED":
            assert True
        else:
            assert fire["constraints"]["position_cap_pct"] <= 0.05
            assert fire["constraints"]["max_trade_freq_per_day"] == 0


@pytest.mark.asyncio
async def test_low_confidence_never_auto_disables():
    """
    Directly exercise the StrategyViabilityDecider policy:
    if confidence < 0.70, it must not auto-disable a strategy.
    """
    app = AgentFieldLiteApp(node_id="risk-governor")
    reasoners_mod.register(app)

    import sqlite3
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    # create minimal memory tables used by search()
    conn.execute("CREATE TABLE memory_kv(scope TEXT, k TEXT, v_json TEXT, updated_at TEXT, PRIMARY KEY(scope,k))")
    conn.execute("CREATE TABLE memory_vectors(vector_id TEXT PRIMARY KEY, scope TEXT, text TEXT, embedding_json TEXT, metadata_json TEXT, created_at TEXT)")
    mem = SqliteMemory(conn)

    regime = {"regime": "crash_risk", "confidence": 0.65, "evidence": {}}
    persona_policy = {
        "persona_id": "p1",
        "max_dd": 0.12,
        "max_vol": 0.22,
        "horizon": "long",
        "panic_likelihood": 0.20,
        "citations": [],
        "confidence": 0.65,
    }
    indicators = {"volatility": 0.25, "max_drawdown": -0.10, "momentum_20d": -0.02, "rsi_14": 45.0, "trend_slope": -0.0005}

    out = await app.call(
        "strategy_viability_decider",
        asset="SPY",
        regime=regime,
        persona_policy=persona_policy,
        indicators=indicators,
        memory=mem,
    )

    v = StrategyViabilityDeciderOut(**out)
    fire = next(d for d in v.decisions if d.strategy_id == "fire")
    assert fire.status == "ENABLED"
    assert fire.constraints.position_cap_pct <= 0.05
    assert fire.constraints.max_trade_freq_per_day == 0

