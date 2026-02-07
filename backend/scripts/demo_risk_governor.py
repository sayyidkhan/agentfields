"""
3-minute demo script: Autonomous Portfolio Risk Governor.

Runs:
1) Create case
2) Normal regime event
3) High vol event
4) Crash risk event
5) Show memory influence via override (panic) then rerun

Usage:
  python backend/scripts/demo_risk_governor.py

Requires service running:
  python -m risk_governor
"""

from __future__ import annotations

import asyncio

import httpx


BASE = "http://127.0.0.1:8090"


async def main() -> None:
    async with httpx.AsyncClient(base_url=BASE, timeout=20.0) as client:
        print("== create case ==")
        r = await client.post(
            "/cases",
            json={
                "asset": "SPY",
                "persona": {
                    "persona_id": "demo_persona",
                    "risk_tolerance": "medium",
                    "time_horizon": "long",
                    "drawdown_sensitivity": "high",
                },
            },
        )
        r.raise_for_status()
        case = r.json()
        case_id = case["case_id"]
        print("case_id:", case_id)

        async def send(event_type: str, severity: float):
            rr = await client.post(
                "/events/market",
                json={
                    "case_id": case_id,
                    "event": {
                        "asset": "SPY",
                        "event_type": event_type,
                        "severity": severity,
                        "details": {"demo": True},
                    },
                },
            )
            rr.raise_for_status()
            out = rr.json()
            guard = out["guard"]
            print(f"\n== event {event_type} sev={severity} ==")
            print("regime:", out["regime"]["regime"], "conf:", out["regime"]["confidence"])
            print("panic_likelihood:", out["persona_policy"]["panic_likelihood"])
            print("fire:", guard["strategies"]["fire"]["status"], guard["strategies"]["fire"]["constraints"])
            print("water:", guard["strategies"]["water"]["status"], guard["strategies"]["water"]["constraints"])
            print("grass:", guard["strategies"]["grass"]["status"], guard["strategies"]["grass"]["constraints"])
            if guard.get("escalations"):
                print("escalation:", guard["escalations"])

        await send("heartbeat", 0.1)
        await send("vol_spike", 0.7)
        await send("crash_signal", 0.85)

        print("\n== simulate user panic override (memory write) ==")
        rr = await client.post(
            "/overrides",
            json={
                "case_id": case_id,
                "asset": "SPY",
                "persona_id": "demo_persona",
                "override_type": "set_cap",
                "strategy_id": "fire",
                "value": 0.05,
                "reason": "panic: reduce exposure",
            },
        )
        rr.raise_for_status()
        print("override stored vector_id:", rr.json()["vector_id"])

        # After panic override, the same high vol should de-risk earlier (memory influences)
        await send("vol_spike", 0.7)

        print("\n== audit report ==")
        rep = await client.get(f"/cases/{case_id}")
        rep.raise_for_status()
        report = rep.json()
        print("runs:", len(report.get("runs", [])))
        if report.get("runs"):
            last = report["runs"][-1]
            print("last_run_audit_id:", last["audit_id"])
            print("citations(sample):", last["citations"][:3])


if __name__ == "__main__":
    asyncio.run(main())

