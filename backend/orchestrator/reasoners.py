"""
MagiStock — Orchestrator Reasoners

The main analysis flow. Coordinates strategy agents in parallel,
stores results in shared memory, and calls the Judge for synthesis.

Each step is a simple decorated function. No DAGs. No YAML. No workflow DSLs.
"""

import asyncio
from agentfield.router import AgentRouter
from shared.schemas import UserPersona

reasoners_router = AgentRouter()


@reasoners_router.reasoner()
async def run_analysis(
    ticker: str = "SPY",
    period_days: int = 252,
    risk_tolerance: str = "medium",
    time_horizon: str = "long",
    drawdown_sensitivity: str = "medium",
) -> dict:
    """
    Main MagiStock analysis flow.

    1. Build user persona
    2. Store persona in shared memory
    3. Run all three strategy agents in parallel (cross-agent calls)
    4. Store results in shared memory
    5. Call Judge to synthesize (cross-agent call)
    6. Return final recommendation

    This is the entry point — call it via:
    POST /api/v1/execute/magistock.run_analysis
    """
    # Access the app through lazy import to avoid circular dependency
    from main import app

    # ── Step 1: Build persona ────────────────────────────────────────────
    persona = UserPersona(
        risk_tolerance=risk_tolerance,
        time_horizon=time_horizon,
        drawdown_sensitivity=drawdown_sensitivity,
    )

    app.note(
        f"""## MagiStock Analysis Started
**Asset:** {ticker}
**Period:** {period_days} days
**Persona:** risk={risk_tolerance}, horizon={time_horizon}, drawdown_sensitivity={drawdown_sensitivity}""",
        tags=["orchestrator", "start"],
    )

    # ── Step 2: Store persona in memory (session scope) ──────────────────
    await app.memory.set("user_persona", persona.model_dump(), scope="session")

    # ── Step 3: Run all strategy agents in parallel ──────────────────────
    app.note("Launching parallel strategy analysis...", tags=["orchestrator"])

    fire_task = app.call(
        "fire-agent.reasoners_run_fire_pipeline",
        ticker=ticker,
        period_days=period_days,
    )
    water_task = app.call(
        "water-agent.reasoners_run_water_pipeline",
        ticker=ticker,
        period_days=period_days,
    )
    grass_task = app.call(
        "grass-agent.reasoners_run_grass_pipeline",
        ticker=ticker,
        period_days=period_days,
    )

    # Parallel execution — all three agents run simultaneously
    fire_result, water_result, grass_result = await asyncio.gather(
        fire_task, water_task, grass_task
    )

    # ── Step 4: Store strategy results in shared memory ──────────────────
    await app.memory.set("fire_result", fire_result)
    await app.memory.set("water_result", water_result)
    await app.memory.set("grass_result", grass_result)
    await app.memory.set("strategy_results", {
        "fire": fire_result,
        "water": water_result,
        "grass": grass_result,
    })

    app.note(
        f"""## Strategy Results Stored
Fire Return: {fire_result.get('backtest', {}).get('total_return', 'N/A')}
Water Return: {water_result.get('backtest', {}).get('total_return', 'N/A')}
Grass Return: {grass_result.get('backtest', {}).get('total_return', 'N/A')}""",
        tags=["orchestrator", "results"],
    )

    # ── Step 5: Judge synthesizes — the persona-aware decision ───────────
    judge_decision = await app.call(
        "judge-agent.reasoners_select_strategy",
        persona=persona.model_dump(),
        fire_result=fire_result,
        water_result=water_result,
        grass_result=grass_result,
    )

    # ── Step 6: Store final recommendation ───────────────────────────────
    await app.memory.set("judge_decision", judge_decision)

    app.note(
        f"""## MagiStock Analysis Complete
**Selected:** {judge_decision.get('selected_agent', 'unknown')}
**Persona Alignment:** {judge_decision.get('persona_alignment_score', 0):.0%}
**Summary:** {judge_decision.get('recommendation_summary', '')[:200]}""",
        tags=["orchestrator", "complete"],
    )

    return {
        "decision": judge_decision,
        "strategies": {
            "fire": fire_result,
            "water": water_result,
            "grass": grass_result,
        },
        "persona": persona.model_dump(),
        "ticker": ticker,
        "period_days": period_days,
    }


@reasoners_router.reasoner()
async def quick_analysis(
    risk_tolerance: str = "medium",
    time_horizon: str = "long",
    drawdown_sensitivity: str = "medium",
) -> dict:
    """
    Convenience endpoint with defaults for quick testing.

    Runs full analysis on SPY with 1 year of data.

    POST /api/v1/execute/magistock.quick_analysis
    """
    return await run_analysis(
        ticker="SPY",
        period_days=252,
        risk_tolerance=risk_tolerance,
        time_horizon=time_horizon,
        drawdown_sensitivity=drawdown_sensitivity,
    )
