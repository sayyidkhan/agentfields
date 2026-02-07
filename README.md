# MagiStock → Autonomous Portfolio Risk Governor (AI Backend)

<img src="img/logo/three-magi.png" alt="Three Magi Logo" width="120">

> **Hackathon framing:** this repo now contains an **AI backend runtime dependency** (AI-as-infrastructure), not a chatbot UI.

## What changed (Before vs After)

### Before (AI at the interface)

```
User → Orchestrator → (Fire/Water/Grass + Judge) → Recommendation
```

### After (AI owns runtime governance)

```
Market event → Risk Governor backend
  → typed reasoning (regime + persona policy + viability + escalation)
  → deterministic action execution (enable/disable/cap only)
  → memory write + audit trail
  → Execution Guard (consumed by downstream trading/execution service)
```

## Litmus test (judge-aligned)

- **System notices first**: market regime shifts, volatility spikes, crash risk, and user panic patterns are detected and stored.
- **Downstream consumes guardrails**: the trading service reads `ExecutionGuard` and stays inside constraints without asking a human.

## AgentField primitives (implemented)

- **Reasoners (typed outputs)**: Pydantic schemas, structured JSON only.
- **Skills (deterministic code)**: market fetch, indicators, backtest, policy application, persistence.
- **Memory (real KV + vector)**: sqlite-backed KV + vector search (deterministic embeddings).
- **Discovery (call-by-name)**: coordinator calls specialist reasoners by name (no hardcoded DAG).

## Backend service (no UI required)

The new backend service is `backend/risk_governor/` (FastAPI).

### API endpoints

- `POST /cases` create evaluation run (asset + persona)
- `POST /events/market` trigger the core loop on a market event
- `GET /decisions/latest?asset=` current execution guard for trading system
- `GET /cases/{id}` full audit report with memory citations
- `POST /overrides` (optional) user override → writes to memory and influences future decisions

## 3-minute demo

Start the backend, then run the demo script (normal → high vol → crash risk, then override → earlier de-risk):

```bash
cd backend
pip install -r requirements.txt
python -m risk_governor
python scripts/demo_risk_governor.py
```

## Project structure (relevant parts)

```
backend/
├── risk_governor/              # ✅ Autonomous Portfolio Risk Governor (NEW)
│   ├── api.py                  # FastAPI endpoints
│   ├── engine.py               # core loop: event → reasoning → actions → memory → persist
│   ├── reasoners.py            # typed reasoners (no free-form text)
│   ├── skills.py               # deterministic skills (no LLM)
│   ├── memory.py               # KV + vector memory (sqlite-backed)
│   └── db.py                   # sqlite schema + persistence helpers
├── shared/                     # deterministic indicators/strategies/data
└── scripts/demo_risk_governor.py
```

> Legacy multi-agent “recommendation” stack (`orchestrator/`, `judge_agent/`, `fire_agent/`, etc.) is still in the repo, but the hackathon-aligned deliverable is the Risk Governor backend.
