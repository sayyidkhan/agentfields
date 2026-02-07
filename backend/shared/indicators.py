"""
MagiStock — Technical Indicators (Skills utility)

Pure computation functions. Same input → same output. Every time.
These are used inside Skills, never in Reasoners.
"""

import numpy as np
from typing import Optional


def sma(prices: list[float], window: int) -> list[Optional[float]]:
    """Simple Moving Average."""
    result = [None] * len(prices)
    arr = np.array(prices)
    for i in range(window - 1, len(arr)):
        result[i] = float(np.mean(arr[i - window + 1 : i + 1]))
    return result


def ema(prices: list[float], window: int) -> list[Optional[float]]:
    """Exponential Moving Average."""
    result = [None] * len(prices)
    arr = np.array(prices, dtype=float)
    multiplier = 2.0 / (window + 1)

    # Start with SMA for first value
    if len(arr) < window:
        return result

    result[window - 1] = float(np.mean(arr[:window]))
    for i in range(window, len(arr)):
        result[i] = (arr[i] - result[i - 1]) * multiplier + result[i - 1]

    return result


def rsi(prices: list[float], window: int = 14) -> list[Optional[float]]:
    """Relative Strength Index (0-100)."""
    result = [None] * len(prices)
    if len(prices) < window + 1:
        return result

    arr = np.array(prices, dtype=float)
    deltas = np.diff(arr)

    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)

    avg_gain = float(np.mean(gains[:window]))
    avg_loss = float(np.mean(losses[:window]))

    for i in range(window, len(deltas)):
        avg_gain = (avg_gain * (window - 1) + gains[i]) / window
        avg_loss = (avg_loss * (window - 1) + losses[i]) / window

        if avg_loss == 0:
            result[i + 1] = 100.0
        else:
            rs = avg_gain / avg_loss
            result[i + 1] = 100.0 - (100.0 / (1.0 + rs))

    # Fill the first RSI value
    if avg_loss == 0:
        result[window] = 100.0
    else:
        rs = float(np.mean(gains[:window])) / float(np.mean(losses[:window]))
        result[window] = 100.0 - (100.0 / (1.0 + rs))

    return result


def bollinger_bands(
    prices: list[float], window: int = 20, num_std: float = 2.0
) -> tuple[list[Optional[float]], list[Optional[float]], list[Optional[float]]]:
    """Bollinger Bands: (upper, middle, lower)."""
    middle = sma(prices, window)
    upper = [None] * len(prices)
    lower = [None] * len(prices)
    arr = np.array(prices, dtype=float)

    for i in range(window - 1, len(arr)):
        std = float(np.std(arr[i - window + 1 : i + 1]))
        if middle[i] is not None:
            upper[i] = middle[i] + num_std * std
            lower[i] = middle[i] - num_std * std

    return upper, middle, lower


def macd(
    prices: list[float], fast: int = 12, slow: int = 26, signal: int = 9
) -> tuple[list[Optional[float]], list[Optional[float]]]:
    """MACD: (macd_line, signal_line)."""
    fast_ema = ema(prices, fast)
    slow_ema = ema(prices, slow)

    macd_line = [None] * len(prices)
    for i in range(len(prices)):
        if fast_ema[i] is not None and slow_ema[i] is not None:
            macd_line[i] = fast_ema[i] - slow_ema[i]

    # Signal line is EMA of MACD values
    valid_macd = [v for v in macd_line if v is not None]
    if len(valid_macd) < signal:
        return macd_line, [None] * len(prices)

    signal_values = ema(valid_macd, signal)
    signal_line = [None] * len(prices)

    valid_idx = 0
    for i in range(len(prices)):
        if macd_line[i] is not None:
            if valid_idx < len(signal_values):
                signal_line[i] = signal_values[valid_idx]
            valid_idx += 1

    return macd_line, signal_line


def rolling_volatility(prices: list[float], window: int = 20) -> list[Optional[float]]:
    """Rolling annualized volatility of returns."""
    result = [None] * len(prices)
    if len(prices) < window + 1:
        return result

    arr = np.array(prices, dtype=float)
    returns = np.diff(np.log(arr))

    for i in range(window, len(returns) + 1):
        vol = float(np.std(returns[i - window : i]) * np.sqrt(252))
        result[i] = vol

    return result


def autocorrelation(prices: list[float], window: int = 20, lag: int = 1) -> list[Optional[float]]:
    """Rolling autocorrelation of returns (used for regime detection)."""
    result = [None] * len(prices)
    if len(prices) < window + lag + 1:
        return result

    arr = np.array(prices, dtype=float)
    returns = np.diff(np.log(arr))

    for i in range(window + lag, len(returns) + 1):
        r = returns[i - window : i]
        r_lagged = returns[i - window - lag : i - lag]
        if len(r) == len(r_lagged) and len(r) > 0:
            corr = float(np.corrcoef(r, r_lagged)[0, 1])
            if not np.isnan(corr):
                result[i] = corr

    return result
