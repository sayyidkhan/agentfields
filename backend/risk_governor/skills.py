from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal, Optional

import numpy as np

from .runtime import AgentFieldLiteApp
from .schemas import StopLossPolicy, StrategyConstraints

# Reuse existing deterministic utilities where possible
from shared.market_data import fetch_market_data as _fetch_prices
from shared.indicators import rsi as _rsi_series, rolling_volatility as _roll_vol_series
from shared.strategies import (
    adaptive_backtest,
    conservative_backtest,
    momentum_backtest,
)


StrategyId = Literal["fire", "water", "grass"]


@dataclass(frozen=True)
class IndicatorSnapshot:
    volatility: float
    max_drawdown: float
    momentum_20d: float
    rsi_14: float
    trend_slope: float


def _max_drawdown(prices: list[float]) -> float:
    if not prices:
        return 0.0
    arr = np.array(prices, dtype=float)
    peak = np.maximum.accumulate(arr)
    dd = (arr - peak) / peak
    return float(np.min(dd)) if dd.size else 0.0


def _momentum(prices: list[float], window: int = 20) -> float:
    if len(prices) < window + 1:
        return 0.0
    start = float(prices[-window - 1])
    end = float(prices[-1])
    if start <= 0:
        return 0.0
    return (end - start) / start


def _trend_slope(prices: list[float], window: int = 30) -> float:
    if len(prices) < window:
        return 0.0
    y = np.array(prices[-window:], dtype=float)
    x = np.arange(window, dtype=float)
    slope = float(np.polyfit(x, y, 1)[0])
    return slope / float(np.mean(y)) if float(np.mean(y)) else 0.0


def register(app: AgentFieldLiteApp) -> None:
    @app.skill(tags=["market"])
    def fetch_market_data(asset: str, window: int = 252) -> dict[str, Any]:
        prices = _fetch_prices(asset, period_days=int(window))
        return {"asset": asset, "window": int(window), "prices": [float(p) for p in prices]}

    @app.skill(tags=["indicators"])
    def compute_indicators(prices: list[float]) -> dict[str, Any]:
        rsi_series = _rsi_series(prices, window=14)
        vol_series = _roll_vol_series(prices, window=20)

        rsi_14 = float(next((v for v in reversed(rsi_series) if v is not None), 50.0))
        vol = float(next((v for v in reversed(vol_series) if v is not None), 0.0))
        dd = float(_max_drawdown(prices))
        mom20 = float(_momentum(prices, window=20))
        slope = float(_trend_slope(prices, window=30))

        snap = IndicatorSnapshot(
            volatility=round(vol, 4),
            max_drawdown=round(dd, 4),
            momentum_20d=round(mom20, 4),
            rsi_14=round(rsi_14, 2),
            trend_slope=round(slope, 6),
        )
        return asdict(snap)

    @app.skill(tags=["backtest"])
    def run_backtest(
        strategy_id: StrategyId,
        prices: list[float],
        constraints: dict[str, Any],
    ) -> dict[str, Any]:
        c = StrategyConstraints(**constraints)

        if strategy_id == "fire":
            base = momentum_backtest(prices).model_dump()
        elif strategy_id == "water":
            base = conservative_backtest(prices).model_dump()
        elif strategy_id == "grass":
            base = adaptive_backtest(prices).model_dump()
        else:
            raise ValueError(f"unknown strategy_id: {strategy_id}")

        # Deterministic "constraint effects" model (hackathon practical):
        # - position cap linearly scales both returns and drawdowns
        cap = float(c.position_cap_pct)
        base["total_return"] = round(float(base["total_return"]) * cap, 4)
        base["max_drawdown"] = round(float(base["max_drawdown"]) * cap, 4)

        # - trade frequency cap reduces trades and slightly smooths volatility
        trades = int(base.get("trades", 0))
        freq_cap = int(c.max_trade_freq_per_day)
        if freq_cap <= 0:
            base["trades"] = 0
            base["total_return"] = round(float(base["total_return"]) * 0.5, 4)
        else:
            # heuristic: treat "per day" cap as a throttle factor
            throttle = min(1.0, max(0.1, freq_cap / 5.0))
            base["trades"] = int(trades * throttle)
            base["volatility"] = round(float(base["volatility"]) * (0.9 + 0.1 * throttle), 4)

        # - stop loss policy reduces drawdown, also reduces return
        sl: StopLossPolicy = c.stop_loss_policy
        if sl.type != "none" and sl.pct is not None:
            pct = float(sl.pct)
            dd_abs = abs(float(base["max_drawdown"]))
            dd_capped = -min(dd_abs, pct)
            base["max_drawdown"] = round(float(dd_capped), 4)
            base["total_return"] = round(float(base["total_return"]) * 0.92, 4)

        return {"strategy_id": strategy_id, "constraints": c.model_dump(), "metrics": base}

    @app.skill(tags=["governance"])
    def apply_policy_constraints(
        strategy_id: StrategyId,
        constraints: dict[str, Any],
        *,
        status: Literal["ENABLED", "DISABLED"],
    ) -> dict[str, Any]:
        c = StrategyConstraints(**constraints)
        return {
            "strategy_id": strategy_id,
            "status": status,
            "constraints": c.model_dump(),
            "allowed_actions": ["enable", "disable", "cap_only"],
        }

    @app.skill(tags=["side_effect"])
    def emit_risk_event(payload: dict[str, Any]) -> dict[str, Any]:
        # Stub: downstream integration point (Kafka/webhook/etc.)
        return {"emitted": True, "payload": payload}

    @app.skill(tags=["side_effect"])
    def notify(payload: dict[str, Any]) -> dict[str, Any]:
        # Stub: send to pager/email/human console
        return {"notified": True, "payload": payload}

