"""
MagiStock — Water Agent Skills

Deterministic functions for conservative / capital-preservation strategy.
"""

from agentfield.router import AgentRouter
from shared.schemas import BacktestResult
from shared.strategies import conservative_backtest
from shared.market_data import fetch_market_data

skills_router = AgentRouter(prefix="skills")


@skills_router.skill(tags=["backtest", "conservative"])
def run_conservative_backtest(
    ticker: str = "SPY",
    period_days: int = 252,
    bb_window: int = 20,
    bb_std: float = 2.0,
) -> dict:
    """
    Execute conservative mean-reversion backtest on historical data.

    Uses Bollinger Bands + RSI for oversold/overbought detection.
    Pure computation. Deterministic.
    """
    prices = fetch_market_data(ticker, period_days)
    result = conservative_backtest(prices, bb_window=bb_window, bb_std=bb_std)
    return result.model_dump()


@skills_router.skill(tags=["metrics"])
def calculate_water_metrics(backtest_result: dict) -> dict:
    """
    Compute additional water-specific metrics from backtest results.

    Focuses on capital preservation: drawdown control, stability, downside risk.
    """
    result = BacktestResult(**backtest_result)

    # Water-specific scoring: heavily rewards low drawdown and low volatility
    preservation_score = min(1.0, max(0.0, 1.0 + result.max_drawdown * 5))  # Less drawdown = higher score
    stability_score = min(1.0, max(0.0, 1.0 - result.volatility * 3))  # Less volatility = higher score

    return {
        "backtest": result.model_dump(),
        "preservation_score": round(preservation_score, 4),
        "stability_score": round(stability_score, 4),
        "strategy_type": "conservative",
        "preferred_regime": "sideways",
    }
