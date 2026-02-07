# MagiStock — Multi-Agent, Persona-Aware Investment Companion

<img src="../img/logo/three-magi.png" alt="Three Magi Logo" width="150">

> **This is the backend.** See [`../frontend/`](../frontend/) for the visualization UI.

> Built on [AgentField.ai](https://agentfield.ai) — Guided Autonomy for Investment Decisions

**MagiStock** is a persona-aware, multi-agent investment decision system. Instead of optimizing for maximum returns, it selects the strategy that **you** can actually stick with.

---

## Architecture

```
    👤 User Persona
         │
    ┌────▼────┐
    │Orchestrator│──── Stores persona in Memory
    └────┬────┘
         │ parallel app.call()
    ┌────┼─────────────┐
    ▼    ▼             ▼
  🔥 Fire  💧 Water  🌱 Grass    ← Strategy Agents
  Agent    Agent     Agent        (independent processes)
    │       │          │
    └───────┼──────────┘
            ▼
     Shared Memory
            │
    ┌───────▼───────┐
    │  ⚖️ Judge Agent │ ← Persona-aware arbiter
    └───────┬───────┘
            ▼
     📊 Recommendation
     (best fit for YOU)
```

### Agents

| Agent | Role | Type |
|-------|------|------|
| **🔥 Fire** | Aggressive momentum strategy | Skills + Reasoners |
| **💧 Water** | Conservative capital-preservation | Skills + Reasoners |
| **🌱 Grass** | Adaptive regime-switching | Skills + Reasoners |
| **⚖️ Judge** | Persona-aware strategy selection | Reasoners only |
| **📊 Orchestrator** | Coordinates everything | Reasoners + Cross-agent calls |

### AgentField Primitives Used

| Primitive | How MagiStock Uses It |
|-----------|----------------------|
| **Reasoners** | Strategy critique, Judge decision, regime detection |
| **Skills** | Backtesting, metric calculation, indicator computation |
| **Memory** | User persona, backtest results, strategy outputs |
| **Discovery** | Judge finds strategy agents, orchestrator coordinates all |

---

## Quick Start

### Prerequisites

- Python 3.10+
- [Agentfield CLI](https://agentfield.ai/docs/quick-start)
- An OpenAI API key (or other LLM provider)

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY
```

### 3. Start Everything

```bash
# Option A: Start all agents at once
chmod +x scripts/start_all.sh
./scripts/start_all.sh

# Option B: Start manually (in separate terminals)
af server                                    # Terminal 1: Control Plane
cd fire_agent && python main.py              # Terminal 2: Fire Agent
cd water_agent && python main.py             # Terminal 3: Water Agent
cd grass_agent && python main.py             # Terminal 4: Grass Agent
cd judge_agent && python main.py             # Terminal 5: Judge Agent
cd orchestrator && python main.py            # Terminal 6: Orchestrator
```

### 4. Run an Analysis

```bash
# Full analysis with custom persona
curl -X POST http://localhost:8080/api/v1/execute/magistock.run_analysis \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "ticker": "SPY",
      "period_days": 252,
      "risk_tolerance": "medium",
      "time_horizon": "long",
      "drawdown_sensitivity": "high"
    }
  }'

# Quick analysis with defaults
curl -X POST http://localhost:8080/api/v1/execute/magistock.quick_analysis \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "risk_tolerance": "low",
      "time_horizon": "long",
      "drawdown_sensitivity": "high"
    }
  }'
```

### 5. Try Different Personas

```bash
# Conservative investor (expects Water agent selection)
curl -X POST http://localhost:8080/api/v1/execute/magistock.run_analysis \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "ticker": "SPY",
      "period_days": 252,
      "risk_tolerance": "low",
      "time_horizon": "long",
      "drawdown_sensitivity": "high"
    }
  }'

# Aggressive investor (expects Fire agent selection)
curl -X POST http://localhost:8080/api/v1/execute/magistock.run_analysis \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "ticker": "SPY",
      "period_days": 252,
      "risk_tolerance": "high",
      "time_horizon": "short",
      "drawdown_sensitivity": "low"
    }
  }'

# Balanced investor (may select Grass agent)
curl -X POST http://localhost:8080/api/v1/execute/magistock.run_analysis \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "ticker": "SPY",
      "period_days": 252,
      "risk_tolerance": "medium",
      "time_horizon": "long",
      "drawdown_sensitivity": "medium"
    }
  }'
```

---

## Project Structure

```
backend/
├── shared/                     # Shared utilities (no AI, no agents)
│   ├── schemas.py              # Pydantic models (all typed outputs)
│   ├── indicators.py           # Technical indicators (SMA, RSI, BB, MACD)
│   ├── market_data.py          # Market data provider (yfinance + synthetic)
│   └── strategies.py           # Backtesting engine (deterministic)
│
├── fire_agent/                 # 🔥 Aggressive Momentum
│   ├── main.py                 # Agent entry point
│   ├── skills.py               # Backtest + metrics (deterministic)
│   └── reasoners.py            # Strategy critique (AI judgment)
│
├── water_agent/                # 💧 Conservative Capital-Preservation
│   ├── main.py
│   ├── skills.py
│   └── reasoners.py
│
├── grass_agent/                # 🌱 Adaptive Regime-Switching
│   ├── main.py
│   ├── skills.py               # Backtest + regime detection (deterministic)
│   └── reasoners.py            # Regime analysis + critique (AI judgment)
│
├── judge_agent/                # ⚖️ Persona-Aware Arbiter
│   ├── main.py
│   └── reasoners.py            # Strategy selection + explanation (AI)
│
├── orchestrator/               # 📊 Main Entry Point
│   ├── main.py
│   └── reasoners.py            # Coordination flow (cross-agent calls)
│
├── scripts/
│   └── start_all.sh            # Start/stop all agents
├── requirements.txt
├── .env.example
└── README.md
```

---

## How It Works

### Reasoner vs Skill Separation

This is the critical AgentField design pattern: **AI decides WHAT to do. Skills DO it.**

```
┌─────────────────────────────┐     ┌──────────────────────────────┐
│         REASONERS           │     │           SKILLS             │
│    (AI judgment calls)      │     │   (deterministic functions)  │
├─────────────────────────────┤     ├──────────────────────────────┤
│ • Strategy critique         │     │ • Backtest execution         │
│ • Market regime detection   │     │ • Metric calculation         │
│ • Judge persona matching    │     │ • Technical indicator math   │
│ • Risk alignment scoring    │     │ • Data fetching & formatting │
│ • Explanation generation    │     │ • Portfolio simulation       │
└─────────────────────────────┘     └──────────────────────────────┘
        Weighs tradeoffs               Same input → same output
        Interprets context              Easy to test, easy to mock
        Typed Pydantic output           No AI, no surprises
```

### Memory Architecture

| Scope | What's Stored | How It's Used |
|-------|--------------|---------------|
| **Session** | User persona | Judge reads it to make persona-aware decisions |
| **Workflow** | Backtest results, critiques | Strategy agents write, Judge reads |
| **Workflow** | Judge decision | Final output stored for retrieval |

### Multi-Agent Flow

1. **Orchestrator** receives user persona + ticker
2. Stores persona in **session memory**
3. Calls all 3 strategy agents **in parallel** via `app.call()`
4. Each strategy agent: **Skill** (backtest) → **Skill** (metrics) → **Reasoner** (critique)
5. Results stored in **shared memory**
6. **Judge** reads all results + persona from memory
7. Judge **Reasoner** selects best-fit strategy (not highest return)
8. Returns structured `JudgeDecision` with reasoning

---

## Technology Stack

- **[AgentField](https://agentfield.ai)** — Reasoners, Skills, Memory, Discovery
- **Python** — Just decorated functions
- **Pydantic** — Typed schemas for all inputs/outputs
- **NumPy** — Backtesting computations (inside Skills)
- **Technical Indicators** — SMA, EMA, RSI, Bollinger Bands, MACD

---

## Why This Matters

MagiStock reframes investing as:
- A **decision support system** — Reasoners weigh tradeoffs, not if-else chains
- A **behavioral alignment problem** — persona stored in Memory, not hardcoded
- A **collaboration between human and AI** — Guided Autonomy, not blind automation

Instead of chasing maximum returns, users learn to choose strategies they can actually stick with.

> *You write Python functions. AgentField handles everything else.*
