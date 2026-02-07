"""
MagiStock — Grass Agent Skills

Deterministic functions for the adaptive regime-switching strategy.
"""

from agentfield.router import AgentRouter
from shared.schemas import BacktestResult
from shared.strategies import adaptive_backtest, detect_regime
from shared.market_data import fetch_market_data

skills_router = AgentRouter(prefix="skills")


@skills_router.skill(tags=["backtest", "adaptive"])
def run_adaptive_backtest(
    ticker: str = "SPY",
    period_days: int = 252,
    regime_window: int = 30,
) -> dict:
    """
    Execute adaptive regime-switching backtest on historical data.

    Switches between momentum and mean-reversion based on market regime.
    Pure computation. Deterministic.
    """
    prices = fetch_market_data(ticker, period_days)
    result = adaptive_backtest(prices, regime_window=regime_window)
    return result.model_dump()


@skills_router.skill(tags=["regime", "analysis"])
def detect_current_regime(ticker: str = "SPY", period_days: int = 252) -> dict:
    """
    Detect the current market regime from price data.

    Returns regime classification and supporting metrics.
    """
    prices = fetch_market_data(ticker, period_days)
    return detect_regime(prices)


@skills_router.skill(tags=["metrics"])
def calculate_grass_metrics(backtest_result: dict, regime_info: dict) -> dict:
    """
    Compute adaptive-specific metrics including regime detection accuracy.
    """
    result = BacktestResult(**backtest_result)

    # Grass-specific scoring: rewards consistency and adaptability
    consistency_score = min(1.0, max(0.0, result.win_rate))
    adaptability_score = min(1.0, max(0.0,
        (1.0 + result.max_drawdown * 3) * 0.5 +  # Drawdown component
        (result.total_return + 0.3) * 0.5  # Return component
    ))

    return {
        "backtest": result.model_dump(),
        "regime": regime_info,
        "consistency_score": round(consistency_score, 4),
        "adaptability_score": round(adaptability_score, 4),
        "strategy_type": "adaptive",
        "preferred_regime": "any",
    }
