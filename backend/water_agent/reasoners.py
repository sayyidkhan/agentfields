"""
MagiStock — Water Agent Reasoners

AI-powered judgment for the conservative capital-preservation strategy.
"""

from agentfield.router import AgentRouter
from shared.schemas import StrategyCritique, BacktestResult

reasoners_router = AgentRouter(prefix="reasoners")


@reasoners_router.reasoner()
async def critique_water_strategy(backtest_result: dict) -> dict:
    """
    AI evaluates the conservative capital-preservation strategy.

    Judges whether this defensive approach provides adequate protection
    while still capturing enough upside to be worthwhile.
    """
    result = BacktestResult(**backtest_result)

    critique = await reasoners_router.ai(
        system="""You are an expert quantitative analyst evaluating a CONSERVATIVE 
        CAPITAL-PRESERVATION strategy. This strategy uses Bollinger Bands and RSI 
        to buy oversold conditions and sell overbought ones, prioritizing 
        capital preservation over returns.
        
        Your job is to critically evaluate:
        1. How well this strategy preserves capital
        2. Whether the returns justify the conservative approach
        3. What market regimes it would protect in vs miss opportunities
        4. Risk alignment — who benefits most from this approach
        
        Be specific with numbers. Be honest about opportunity costs.""",

        user=f"""Evaluate this conservative capital-preservation strategy result:
        
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
async def run_water_pipeline(ticker: str = "SPY", period_days: int = 252) -> dict:
    """
    Full Water Agent pipeline: Backtest → Metrics → Critique.

    This is the entry point called by the Orchestrator.
    """
    from skills import run_conservative_backtest, calculate_water_metrics

    # Step 1: Skill — run backtest (deterministic)
    backtest_raw = run_conservative_backtest(ticker=ticker, period_days=period_days)

    # Step 2: Skill — calculate water-specific metrics (deterministic)
    metrics = calculate_water_metrics(backtest_raw)

    # Step 3: Reasoner — AI critique (judgment call)
    critique = await critique_water_strategy(backtest_raw)

    return {
        "agent_name": "water",
        "backtest": backtest_raw,
        "metrics": metrics,
        "critique": critique,
    }
