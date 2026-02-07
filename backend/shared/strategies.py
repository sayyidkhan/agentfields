"""
MagiStock — Backtesting Strategies (Skill utility)

Pure computation. Same input → same output. Every time.
These functions are used inside Skills — no AI, no surprises.
"""

import numpy as np
from .indicators import sma, rsi, bollinger_bands, ema, rolling_volatility, autocorrelation
from .schemas import BacktestResult


# ─── Portfolio Simulator ─────────────────────────────────────────────────────

def _simulate_portfolio(
    prices: list[float],
    signals: list[int],
    initial_capital: float = 10000.0,
) -> BacktestResult:
    """
    Simulate a portfolio based on trading signals.

    signals: list of int where 1 = buy/hold, 0 = cash, -1 = sell/short
    Returns BacktestResult with all performance metrics.
    """
    capital = initial_capital
    position = 0.0  # Number of shares held
    trades = 0
    trade_returns = []
    entry_price = 0.0
    portfolio_values = [initial_capital]

    for i in range(1, len(prices)):
        signal = signals[i] if i < len(signals) else 0

        if signal == 1 and position == 0:
            # Buy
            position = capital / prices[i]
            entry_price = prices[i]
            capital = 0.0
            trades += 1
        elif signal <= 0 and position > 0:
            # Sell
            capital = position * prices[i]
            trade_return = (prices[i] - entry_price) / entry_price
            trade_returns.append(trade_return)
            position = 0.0

        # Track portfolio value
        if position > 0:
            portfolio_values.append(position * prices[i])
        else:
            portfolio_values.append(capital)

    # Close any open position
    if position > 0:
        capital = position * prices[-1]
        trade_return = (prices[-1] - entry_price) / entry_price
        trade_returns.append(trade_return)
        portfolio_values[-1] = capital

    # Calculate metrics
    portfolio_arr = np.array(portfolio_values)
    daily_returns = np.diff(portfolio_arr) / portfolio_arr[:-1]
    daily_returns = daily_returns[~np.isnan(daily_returns)]

    total_return = (portfolio_values[-1] - initial_capital) / initial_capital

    # Max drawdown
    peak = np.maximum.accumulate(portfolio_arr)
    drawdowns = (portfolio_arr - peak) / peak
    max_drawdown = float(np.min(drawdowns)) if len(drawdowns) > 0 else 0.0

    # Annualized volatility
    volatility = float(np.std(daily_returns) * np.sqrt(252)) if len(daily_returns) > 0 else 0.0

    # Sharpe ratio (assuming risk-free rate of 4%)
    risk_free_daily = 0.04 / 252
    excess_returns = daily_returns - risk_free_daily
    sharpe = float(np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)) if np.std(excess_returns) > 0 else 0.0

    # Win rate
    winning = [r for r in trade_returns if r > 0]
    win_rate = len(winning) / len(trade_returns) if trade_returns else 0.0

    # Average trade return
    avg_trade_return = float(np.mean(trade_returns)) if trade_returns else 0.0

    return BacktestResult(
        total_return=round(total_return, 4),
        max_drawdown=round(max_drawdown, 4),
        volatility=round(volatility, 4),
        sharpe_ratio=round(sharpe, 2),
        trades=trades,
        win_rate=round(win_rate, 4),
        avg_trade_return=round(avg_trade_return, 4),
    )


# ─── Momentum Strategy (Fire Agent) ─────────────────────────────────────────

def momentum_backtest(
    prices: list[float],
    fast_window: int = 10,
    slow_window: int = 30,
    rsi_window: int = 14,
) -> BacktestResult:
    """
    Momentum / trend-following strategy.

    Buy signal: Fast SMA crosses above Slow SMA AND RSI > 50
    Sell signal: Fast SMA crosses below Slow SMA OR RSI < 40

    Aggressive — favors trending markets, accepts high drawdowns.
    """
    fast_sma = sma(prices, fast_window)
    slow_sma = sma(prices, slow_window)
    rsi_values = rsi(prices, rsi_window)

    signals = [0] * len(prices)
    min_lookback = max(fast_window, slow_window, rsi_window + 1)

    for i in range(min_lookback, len(prices)):
        if fast_sma[i] is None or slow_sma[i] is None or rsi_values[i] is None:
            continue

        # Buy: golden cross + RSI confirmation
        if fast_sma[i] > slow_sma[i] and rsi_values[i] > 50:
            signals[i] = 1
        # Sell: death cross or RSI oversold warning
        elif fast_sma[i] < slow_sma[i] or rsi_values[i] < 40:
            signals[i] = 0
        else:
            signals[i] = signals[i - 1]  # Hold previous position

    return _simulate_portfolio(prices, signals)


# ─── Conservative Strategy (Water Agent) ─────────────────────────────────────

def conservative_backtest(
    prices: list[float],
    bb_window: int = 20,
    bb_std: float = 2.0,
    rsi_window: int = 14,
) -> BacktestResult:
    """
    Capital-preservation / mean-reversion strategy.

    Buy signal: Price near lower Bollinger Band AND RSI < 30 (oversold)
    Sell signal: Price near upper Bollinger Band OR RSI > 70 (overbought)

    Conservative — minimizes drawdown, favors sideways markets.
    """
    upper, middle, lower = bollinger_bands(prices, bb_window, bb_std)
    rsi_values = rsi(prices, rsi_window)

    signals = [0] * len(prices)
    min_lookback = max(bb_window, rsi_window + 1)

    for i in range(min_lookback, len(prices)):
        if lower[i] is None or upper[i] is None or rsi_values[i] is None:
            continue

        # Buy: oversold near lower band
        if prices[i] <= lower[i] * 1.02 and rsi_values[i] < 35:
            signals[i] = 1
        # Sell: overbought near upper band
        elif prices[i] >= upper[i] * 0.98 or rsi_values[i] > 70:
            signals[i] = 0
        else:
            signals[i] = signals[i - 1]  # Hold previous position

    return _simulate_portfolio(prices, signals)


# ─── Adaptive Strategy (Grass Agent) ─────────────────────────────────────────

def adaptive_backtest(
    prices: list[float],
    regime_window: int = 30,
    fast_window: int = 10,
    slow_window: int = 30,
    bb_window: int = 20,
) -> BacktestResult:
    """
    Regime-switching adaptive strategy.

    Detects market regime and switches approach:
    - Trending: Use momentum (fast/slow SMA crossover)
    - Mean-reverting: Use Bollinger Band mean-reversion
    - High volatility: Stay in cash

    Balanced — adjusts to market conditions, moderate risk.
    """
    vol = rolling_volatility(prices, regime_window)
    autocorr = autocorrelation(prices, regime_window)
    fast_sma = sma(prices, fast_window)
    slow_sma = sma(prices, slow_window)
    upper, middle, lower = bollinger_bands(prices, bb_window)
    rsi_values = rsi(prices)

    signals = [0] * len(prices)
    min_lookback = max(regime_window + 1, slow_window, bb_window)

    for i in range(min_lookback, len(prices)):
        current_vol = vol[i]
        current_autocorr = autocorr[i] if i < len(autocorr) else None

        if current_vol is None:
            continue

        # Detect regime
        if current_vol > 0.30:
            # High volatility → stay in cash
            signals[i] = 0
        elif current_autocorr is not None and current_autocorr > 0.1:
            # Positive autocorrelation → trending → use momentum
            if fast_sma[i] is not None and slow_sma[i] is not None:
                if fast_sma[i] > slow_sma[i]:
                    signals[i] = 1
                else:
                    signals[i] = 0
            else:
                signals[i] = signals[i - 1]
        else:
            # Low autocorrelation → mean-reverting → use Bollinger
            if lower[i] is not None and upper[i] is not None and rsi_values[i] is not None:
                if prices[i] <= lower[i] * 1.02 and rsi_values[i] < 40:
                    signals[i] = 1
                elif prices[i] >= upper[i] * 0.98 or rsi_values[i] > 65:
                    signals[i] = 0
                else:
                    signals[i] = signals[i - 1]
            else:
                signals[i] = signals[i - 1]

    return _simulate_portfolio(prices, signals)


def detect_regime(prices: list[float], window: int = 30) -> dict:
    """
    Detect the current market regime from price data.

    Returns a dict with regime info for the Grass agent's Reasoner to analyze.
    """
    if len(prices) < window + 2:
        return {
            "regime": "unknown",
            "volatility": 0.0,
            "autocorrelation": 0.0,
            "trend_strength": 0.0,
        }

    arr = np.array(prices, dtype=float)
    returns = np.diff(np.log(arr))
    recent_returns = returns[-window:]

    current_vol = float(np.std(recent_returns) * np.sqrt(252))

    # Autocorrelation
    if len(recent_returns) > 1:
        r1 = recent_returns[:-1]
        r2 = recent_returns[1:]
        current_autocorr = float(np.corrcoef(r1, r2)[0, 1])
        if np.isnan(current_autocorr):
            current_autocorr = 0.0
    else:
        current_autocorr = 0.0

    # Trend strength (slope of linear regression on prices)
    recent_prices = arr[-window:]
    x = np.arange(window)
    slope = float(np.polyfit(x, recent_prices, 1)[0])
    trend_strength = slope / np.mean(recent_prices) * 252  # Annualized

    # Classify regime
    if current_vol > 0.30:
        regime = "high_volatility"
    elif abs(trend_strength) > 0.15 and current_autocorr > 0.05:
        regime = "trending_up" if trend_strength > 0 else "trending_down"
    else:
        regime = "mean_reverting"

    return {
        "regime": regime,
        "volatility": round(float(current_vol), 4),
        "autocorrelation": round(float(current_autocorr), 4),
        "trend_strength": round(float(trend_strength), 4),
    }
