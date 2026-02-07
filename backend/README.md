# MagiStock Backend — Autonomous Portfolio Risk Governor

This backend now includes a **Risk Governor service**: an AI backend reasoning layer that continuously governs which strategies are allowed to operate and under what constraints. A downstream execution/trading service consumes the resulting `ExecutionGuard`.

## New architecture (judge-aligned)

```
Market event
  → typed Reasoners (regime → persona policy → viability → escalation)
  → deterministic Skills (fetch → indicators → backtest → apply constraints)
  → Memory write (KV + vector) + Audit persistence (sqlite)
  → ExecutionGuard (downstream runtime contract)
```

## Quick start (Risk Governor service)

```bash
cd backend
pip install -r requirements.txt
python -m risk_governor
```

Service listens on `http://127.0.0.1:8090`.

## API

- `POST /cases`
- `POST /events/market`
- `GET /decisions/latest?asset=SPY`
- `GET /cases/{case_id}`
- `POST /overrides` (optional)

## Demo mode

```bash
python scripts/demo_risk_governor.py
```

## Notes

- The original multi-agent “recommendation” system (Orchestrator/Judge/Fire/Water/Grass agents) remains in this repo for reference.
- The hackathon deliverable is the **Risk Governor backend** in `backend/risk_governor/`.
