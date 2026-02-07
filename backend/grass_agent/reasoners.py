"""
MagiStock — Grass Agent Reasoners

AI-powered judgment for the adaptive strategy.
Includes both strategy critique AND market regime analysis.
"""

from agentfield.router import AgentRouter
from shared.schemas import StrategyCritique, MarketRegime, BacktestResult

reasoners_router = AgentRouter(prefix="reasoners")


@reasoners_router.reasoner()
async def detect_market_regime(regime_data: dict) -> dict:
    """
    AI analyzes market indicators to classify the current regime.

    This is a REASONER because regime classification involves judgment:
    - Is this volatility temporary or structural?
    - Is the trend strong enough to trade on?
    - Are conditions changing?
    """
    regime = await reasoners_router.ai(
        system="""You are an expert market regime analyst. Given quantitative indicators,
        classify the current market regime and recommend a trading approach.
        
        Regimes:
        - trending_up: Strong upward momentum, positive autocorrelation
        - trending_down: Strong downward momentum, negative trend
        - mean_reverting: Low autocorrelation, prices oscillate around mean
        - high_volatility: Elevated volatility, uncertain direction
        
        Be specific about your confidence and reasoning.""",

        user=f"""Analyze these market indicators:
        
        Detected Regime: {regime_data.get('regime', 'unknown')}
        Annualized Volatility: {regime_data.get('volatility', 0):.2%}
        Return Autocorrelation: {regime_data.get('autocorrelation', 0):.4f}
        Trend Strength (annualized): {regime_data.get('trend_strength', 0):.2%}
        
        Classify the regime, explain your reasoning, and recommend an approach.""",

        schema=MarketRegime,
    )
    return regime.model_dump()


@reasoners_router.reasoner()
async def critique_grass_strategy(backtest_result: dict, regime_data: dict) -> dict:
    """
    AI evaluates the adaptive strategy's performance AND regime detection accuracy.
    """
    result = BacktestResult(**backtest_result)

    critique = await reasoners_router.ai(
        system="""You are an expert quantitative analyst evaluating an ADAPTIVE 
        REGIME-SWITCHING strategy. This strategy detects market conditions and 
        switches between momentum (for trends) and mean-reversion (for ranging markets),
        going to cash during high-volatility periods.
        
        Your job is to evaluate:
        1. Overall performance quality
        2. How well the regime switching worked
        3. Whether the adaptability justified the complexity
        4. Risk/reward balance across different conditions
        
        Be specific. Consider that adaptability has costs (whipsaws, lag).""",

        user=f"""Evaluate this adaptive regime-switching strategy:
        
        Total Return: {result.total_return:.2%}
        Max Drawdown: {result.max_drawdown:.2%}
        Annualized Volatility: {result.volatility:.2%}
        Sharpe Ratio: {result.sharpe_ratio:.2f}
        Total Trades: {result.trades}
        Win Rate: {result.win_rate:.1%}
        Avg Trade Return: {result.avg_trade_return:.2%}
        
        Current Regime Info:
        Regime: {regime_data.get('regime', 'unknown')}
        Volatility: {regime_data.get('volatility', 0):.2%}
        Autocorrelation: {regime_data.get('autocorrelation', 0):.4f}
        
        Assess: regime suitability, risk alignment, strengths, weaknesses.""",

        schema=StrategyCritique,
    )
    return critique.model_dump()


@reasoners_router.reasoner()
async def run_grass_pipeline(ticker: str = "SPY", period_days: int = 252) -> dict:
    """
    Full Grass Agent pipeline: Regime Detection → Backtest → Metrics → Critique.

    This is the entry point called by the Orchestrator.
    """
    from skills import detect_current_regime, run_adaptive_backtest, calculate_grass_metrics

    # Step 1: Skill — detect market regime (deterministic indicators)
    regime_data = detect_current_regime(ticker=ticker, period_days=period_days)

    # Step 2: Reasoner — AI analyzes the regime (judgment call)
    regime_analysis = await detect_market_regime(regime_data)

    # Step 3: Skill — run adaptive backtest (deterministic)
    backtest_raw = run_adaptive_backtest(ticker=ticker, period_days=period_days)

    # Step 4: Skill — calculate grass-specific metrics (deterministic)
    metrics = calculate_grass_metrics(backtest_raw, regime_data)

    # Step 5: Reasoner — AI critique (judgment call)
    critique = await critique_grass_strategy(backtest_raw, regime_data)

    return {
        "agent_name": "grass",
        "backtest": backtest_raw,
        "metrics": metrics,
        "regime": regime_analysis,
        "critique": critique,
    }
