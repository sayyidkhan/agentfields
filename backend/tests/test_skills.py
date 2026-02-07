import sys
from pathlib import Path

import pytest


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


from risk_governor.runtime import AgentFieldLiteApp
from risk_governor import skills as skills_mod


@pytest.fixture()
def app():
    a = AgentFieldLiteApp(node_id="risk-governor")
    skills_mod.register(a)
    return a


def test_compute_indicators_is_deterministic(app):
    prices = [100.0 + i * 0.5 for i in range(300)]
    out1 = app._skills["risk-governor.skills.compute_indicators"].fn(prices=prices)
    out2 = app._skills["risk-governor.skills.compute_indicators"].fn(prices=prices)
    assert out1 == out2
    assert "volatility" in out1
    assert "max_drawdown" in out1
    assert "momentum_20d" in out1
    assert "rsi_14" in out1


def test_run_backtest_returns_metrics(app):
    prices = [100.0 + (i % 10) * 0.2 for i in range(300)]
    constraints = {
        "position_cap_pct": 0.25,
        "max_trade_freq_per_day": 2,
        "stop_loss_policy": {"type": "fixed_pct", "pct": 0.10},
    }
    out = app._skills["risk-governor.skills.run_backtest"].fn(
        strategy_id="fire", prices=prices, constraints=constraints
    )
    assert out["strategy_id"] == "fire"
    assert "metrics" in out
    assert "total_return" in out["metrics"]
    assert "max_drawdown" in out["metrics"]

