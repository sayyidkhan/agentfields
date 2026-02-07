"""
MagiStock — Fire Agent Skills

Deterministic functions. Same input → same output. No AI, no surprises.
"""

from agentfield.router import AgentRouter
from shared.schemas import BacktestResult
from shared.strategies import momentum_backtest
from shared.market_data import fetch_market_data

skills_router = AgentRouter(prefix="skills")


@skills_router.skill(tags=["backtest", "momentum"])
def run_momentum_backtest(
    ticker: str = "SPY",
    period_days: int = 252,
    fast_window: int = 10,
    slow_window: int = 30,
) -> dict:
    """
    Execute momentum strategy backtest on historical data.

    Pure computation. Deterministic. Testable.
    """
    prices = fetch_market_data(ticker, period_days)
    result = momentum_backtest(prices, fast_window=fast_window, slow_window=slow_window)
    return result.model_dump()


@skills_router.skill(tags=["metrics"])
def calculate_fire_metrics(backtest_result: dict) -> dict:
    """
    Compute additional fire-specific metrics from backtest results.

    Focuses on momentum-specific indicators like upside capture and trend strength.
    """
    result = BacktestResult(**backtest_result)

    # Fire-specific scoring: rewards high returns, penalizes less for drawdowns
    aggression_score = min(1.0, max(0.0, (result.total_return + 0.5) / 1.0))
    risk_reward = abs(result.total_return / result.max_drawdown) if result.max_drawdown != 0 else 0.0

    return {
        "backtest": result.model_dump(),
        "aggression_score": round(aggression_score, 4),
        "risk_reward_ratio": round(risk_reward, 4),
        "strategy_type": "momentum",
        "preferred_regime": "trending",
    }
