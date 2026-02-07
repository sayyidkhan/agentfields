# MagiStock

<img src="img/logo/three-magi.png" alt="Three Magi Logo" width="120">

> A persona-aware, multi-agent investment companion built on [AgentField.ai](https://agentfield.ai)

MagiStock doesn't optimize for maximum returns. It selects the strategy that **you** can actually stick with.

---

## Architecture

```
    👤 User (Frontend)
         │
    ┌────▼─────────┐
    │  Orchestrator │──── Stores persona in Memory
    └────┬─────────┘
         │ parallel app.call()
    ┌────┼─────────────┐
    ▼    ▼             ▼
  🔥 Fire  💧 Water  🌱 Grass    ← Strategy Agents (Skills + Reasoners)
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
```

## Project Structure

```
agentfields/
├── backend/                    # Agentfield multi-agent system
│   ├── shared/                 # Schemas, indicators, strategies
│   ├── fire_agent/             # 🔥 Aggressive momentum
│   ├── water_agent/            # 💧 Conservative preservation
│   ├── grass_agent/            # 🌱 Adaptive regime-switching
│   ├── judge_agent/            # ⚖️  Persona-aware arbiter
│   ├── orchestrator/           # 📊 Coordination & parallel execution
│   └── scripts/start_all.sh
│
├── frontend/                   # React visualization UI
│   └── src/
│       ├── components/         # PersonaForm, StrategyCard, JudgeDecision, etc.
│       ├── api.ts              # Agentfield REST API client
│       └── App.tsx             # Multi-step user journey
│
├── docs/                       # AgentField documentation
├── img/                        # Logos and assets
└── idea-1-enhanced.md          # Original PRD
```

## Quick Start

### Backend (Agentfield Agents)

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env            # Set your OPENAI_API_KEY
chmod +x scripts/start_all.sh
./scripts/start_all.sh          # Starts control plane + 5 agents
```

### Frontend (Visualization)

```bash
cd frontend
npm install
npm run dev                     # http://localhost:3000
```

The frontend starts in **mock mode** by default (no backend needed). Set `USE_MOCK = false` in `src/App.tsx` to connect to the live Agentfield backend.

## How It Works

1. **You** describe your risk profile (3 simple questions)
2. **Three strategy agents** run backtests in parallel, each with a different philosophy
3. **Each agent critiques** its own performance using AI (Reasoners)
4. **The Judge** weighs all results against your persona — not just returns
5. **You get** a personalized recommendation with honest tradeoffs

## Tech Stack

- **[AgentField](https://agentfield.ai)** — Reasoners, Skills, Memory, Discovery
- **Python** + **Pydantic** — Backend agents with typed schemas
- **React** + **TypeScript** + **Tailwind CSS** — Frontend visualization
- **NumPy** — Deterministic backtesting inside Skills
