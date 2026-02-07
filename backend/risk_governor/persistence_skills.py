from __future__ import annotations

from datetime import datetime
from typing import Any

from .db import insert_audit, insert_decision
from .runtime import AgentFieldLiteApp


def register(app: AgentFieldLiteApp) -> None:
    @app.skill(tags=["persistence"])
    def persist_decision(
        *,
        conn: Any,  # sqlite3.Connection
        decision_id: str,
        case_id: str,
        asset: str,
        guard: dict[str, Any],
        audit_id: str,
        as_of: str | None = None,
    ) -> dict[str, Any]:
        ts = as_of or datetime.utcnow().isoformat()
        insert_decision(
            conn,
            decision_id=decision_id,
            case_id=case_id,
            asset=asset,
            as_of=ts,
            guard=guard,
            audit_id=audit_id,
        )
        return {"persisted": True, "decision_id": decision_id, "as_of": ts}

    @app.skill(tags=["persistence"])
    def persist_audit(
        *,
        conn: Any,  # sqlite3.Connection
        audit_id: str,
        case_id: str,
        asset: str,
        report: dict[str, Any],
        created_at: str | None = None,
    ) -> dict[str, Any]:
        ts = created_at or datetime.utcnow().isoformat()
        insert_audit(
            conn,
            audit_id=audit_id,
            case_id=case_id,
            asset=asset,
            created_at=ts,
            report=report,
        )
        return {"persisted": True, "audit_id": audit_id, "created_at": ts}

