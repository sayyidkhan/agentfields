from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException, Query

from .db import SqliteDB, get_case, get_case_audits, insert_case
from .memory import SqliteMemory
from .schemas import (
    CaseCreateRequest,
    CaseCreateResponse,
    MarketEventIn,
    OverrideRequest,
    RunDecision,
)
from .service import build_engine


def _json_loads(s: str) -> Any:
    return json.loads(s)


engine = build_engine()

app = FastAPI(title="Autonomous Portfolio Risk Governor", version="0.1.0")


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/cases", response_model=CaseCreateResponse)
def create_case(req: CaseCreateRequest):
    case_id = f"case_{uuid.uuid4().hex}"
    created_at = datetime.utcnow()
    inputs = req.model_dump()

    from pathlib import Path

    SqliteDB(Path(engine.db_path)).migrate()

    import sqlite3

    conn = sqlite3.connect(engine.db_path)
    conn.row_factory = sqlite3.Row
    with conn:
        insert_case(
            conn,
            case_id=case_id,
            asset=req.asset,
            persona_id=req.persona.persona_id,
            created_at=created_at.isoformat(),
            inputs=inputs,
        )

        # Seed persona behavior KV (real memory, not conceptual)
        mem = SqliteMemory(conn)
        scope = f"persona:{req.persona.persona_id}"
        if mem.get(scope, "behavior") is None:
            mem.set(scope, "behavior", {"panic_events": 0, "overrides": 0, "last_panic_drawdown": 0.0})

    return CaseCreateResponse(
        case_id=case_id,
        asset=req.asset,
        persona_id=req.persona.persona_id,
        created_at=created_at,
    )


@app.post("/events/market", response_model=RunDecision)
async def market_event(payload: MarketEventIn):
    try:
        return await engine.process_market_event(case_id=payload.case_id, event=payload.event)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/decisions/latest")
def latest_decision(asset: str = Query(..., description="Asset identifier")):
    g = engine.get_latest_guard(asset)
    if g is None:
        raise HTTPException(status_code=404, detail="no decision for asset")
    return g


@app.get("/cases/{case_id}")
def get_case_report(case_id: str):
    import sqlite3

    conn = sqlite3.connect(engine.db_path)
    conn.row_factory = sqlite3.Row
    with conn:
        case = get_case(conn, case_id)
        if case is None:
            raise HTTPException(status_code=404, detail="case not found")
        audits = get_case_audits(conn, case_id)
        if not audits:
            # case exists, but no run yet
            return {
                "case_id": case_id,
                "asset": case["asset"],
                "created_at": case["created_at"],
                "runs": [],
            }

        runs = []
        for a in audits:
            runs.append(
                {
                    "audit_id": a["audit_id"],
                    "created_at": a["created_at"],
                    "inputs": _json_loads(a["inputs_json"]),
                    "memory_reads": _json_loads(a["memory_reads_json"]),
                    "memory_writes": _json_loads(a["memory_writes_json"]),
                    "reasoner_outputs": _json_loads(a["reasoner_outputs_json"]),
                    "selected_actions": _json_loads(a["selected_actions_json"]),
                    "citations": _json_loads(a["citations_json"]),
                }
            )

        return {
            "case_id": case_id,
            "asset": case["asset"],
            "created_at": case["created_at"],
            "inputs": _json_loads(case["inputs_json"]),
            "runs": runs,
        }


@app.post("/overrides")
def override(req: OverrideRequest):
    """
    Optional: user override that writes to memory and impacts future decisions.
    """
    import sqlite3

    conn = sqlite3.connect(engine.db_path)
    conn.row_factory = sqlite3.Row
    with conn:
        mem = SqliteMemory(conn)
        scope = f"persona:{req.persona_id}"
        behavior = mem.get(scope, "behavior") or {"panic_events": 0, "overrides": 0, "last_panic_drawdown": 0.0}
        behavior["overrides"] = int(behavior.get("overrides", 0)) + 1
        mem.set(scope, "behavior", behavior)

        # vector memory: store override moment as "incident-like" event
        vec_scope = f"asset:{req.asset}"
        text = f"override asset={req.asset} persona={req.persona_id} type={req.override_type} strategy={req.strategy_id} value={req.value} reason={req.reason}"
        vec_id = mem.add_vector(vec_scope, text, metadata=req.model_dump())

        # kv: store last override
        mem.set(scope, "last_override", {"at": req.occurred_at.isoformat(), **req.model_dump()})

    return {"ok": True, "vector_id": vec_id}

