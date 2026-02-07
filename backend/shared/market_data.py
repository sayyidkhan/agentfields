"""
MagiStock — Market Data Provider (Skill utility)

Provides historical price data for backtesting.
Falls back to synthetic data if yfinance is not available.
"""

import numpy as np
from datetime import datetime, timedelta


def fetch_market_data(ticker: str = "SPY", period_days: int = 252) -> list[float]:
    """
    Fetch historical daily closing prices.

    Tries yfinance first, falls back to realistic synthetic data.
    This is a Skill utility — deterministic for the same inputs when using synthetic data.
    """
    try:
        return _fetch_from_yfinance(ticker, period_days)
    except Exception:
        return _generate_synthetic_data(ticker, period_days)


def _fetch_from_yfinance(ticker: str, period_days: int) -> list[float]:
    """Fetch from Yahoo Finance using yfinance."""
    import yfinance as yf

    end_date = datetime.now()
    start_date = end_date - timedelta(days=int(period_days * 1.5))  # Buffer for weekends

    data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    if data.empty:
        raise ValueError(f"No data returned for {ticker}")

    prices = data["Close"].dropna().tolist()[-period_days:]
    if len(prices) < period_days // 2:
        raise ValueError(f"Insufficient data for {ticker}")

    return [float(p) for p in prices]


def _generate_synthetic_data(ticker: str, period_days: int) -> list[float]:
    """
    Generate realistic synthetic market data using geometric Brownian motion.

    Seeded by ticker name for reproducibility (same ticker → same data).
    """
    # Seed based on ticker for reproducibility
    seed = sum(ord(c) for c in ticker) * 42
    rng = np.random.RandomState(seed)

    # Market parameters (realistic for equity indices)
    initial_price = {
        "SPY": 450.0,
        "BTC": 45000.0,
        "QQQ": 380.0,
        "IWM": 200.0,
    }.get(ticker.upper(), 100.0)

    annual_return = 0.08  # 8% average annual return
    annual_vol = 0.18  # 18% annual volatility

    # Convert to daily
    daily_return = annual_return / 252
    daily_vol = annual_vol / np.sqrt(252)

    # Generate with regime changes for realism
    prices = [initial_price]
    regime_length = period_days // 4

    for day in range(1, period_days):
        # Shift regime every quarter
        regime = day // regime_length
        if regime % 4 == 0:
            # Bull market
            mu = daily_return * 1.5
            sigma = daily_vol * 0.8
        elif regime % 4 == 1:
            # High volatility
            mu = daily_return * 0.2
            sigma = daily_vol * 1.8
        elif regime % 4 == 2:
            # Bear market
            mu = -daily_return * 0.5
            sigma = daily_vol * 1.3
        else:
            # Recovery
            mu = daily_return * 1.2
            sigma = daily_vol * 1.0

        # Geometric Brownian motion
        shock = rng.normal(mu, sigma)
        new_price = prices[-1] * np.exp(shock)
        prices.append(float(new_price))

    return prices


def get_date_range(period_days: int) -> list[str]:
    """Generate a list of trading dates (business days) for display."""
    end_date = datetime.now()
    dates = []
    current = end_date - timedelta(days=int(period_days * 1.5))

    while len(dates) < period_days:
        if current.weekday() < 5:  # Monday to Friday
            dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    return dates[-period_days:]
