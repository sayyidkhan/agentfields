"""
MagiStock — Fire Agent Reasoners

AI-powered judgment. Evaluates whether the aggressive momentum approach
suits the current market conditions. Weighs tradeoffs. Interprets context.
"""

from agentfield.router import AgentRouter
from shared.schemas import StrategyCritique, BacktestResult

reasoners_router = AgentRouter(prefix="reasoners")


@reasoners_router.reasoner()
async def critique_fire_strategy(backtest_result: dict) -> dict:
    """
    AI evaluates the aggressive momentum strategy performance.

    This is the core judgment call — not whether the numbers are good,
    but whether THIS approach is suitable given what the data shows.
    """
    result = BacktestResult(**backtest_result)

    critique = await reasoners_router.ai(
        system="""You are an expert quantitative analyst evaluating an AGGRESSIVE MOMENTUM 
        trading strategy. This strategy uses fast/slow SMA crossovers with RSI confirmation 
        to capture trending markets.
        
        Your job is to critically evaluate:
        1. How well this strategy performed
        2. What market regimes it would excel in vs struggle
        3. Risk alignment — who should and shouldn't use this
        4. Honest strengths and weaknesses
        
        Be specific with numbers. Be honest about risks.""",

        user=f"""Evaluate this aggressive momentum strategy result:
        
        Total Return: {result.total_return:.2%}
        Max Drawdown: {result.max_drawdown:.2%}
        Annualized Volatility: {result.volatility:.2%}
        Sharpe Ratio: {result.sharpe_ratio:.2f}
        Total Trades: {result.trades}
        Win Rate: {result.win_rate:.1%}
        Avg Trade Return: {result.avg_trade_return:.2%}
        
        Assess: regime suitability, risk alignment, key strengths, key weaknesses.
        Rate your confidence in this strategy on a 0-1 scale.""",

        schema=StrategyCritique,
    )
    return critique.model_dump()


@reasoners_router.reasoner()
async def run_fire_pipeline(ticker: str = "SPY", period_days: int = 252) -> dict:
    """
    Full Fire Agent pipeline: Backtest → Metrics → Critique.

    This is the entry point called by the Orchestrator.
    Skills gather data → Reasoner judges.
    """
    from skills import run_momentum_backtest, calculate_fire_metrics

    # Step 1: Skill — run backtest (deterministic)
    backtest_raw = run_momentum_backtest(ticker=ticker, period_days=period_days)

    # Step 2: Skill — calculate fire-specific metrics (deterministic)
    metrics = calculate_fire_metrics(backtest_raw)

    # Step 3: Reasoner — AI critique (judgment call)
    critique = await critique_fire_strategy(backtest_raw)

    return {
        "agent_name": "fire",
        "backtest": backtest_raw,
        "metrics": metrics,
        "critique": critique,
    }
