"""
Fetch stock time-series (OHLCV) for a ticker and time period.

Data source: Yahoo Finance via yfinance (no API key required).
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date

import pandas as pd
import yfinance as yf


def _is_empty_or_whitespace(s: str | None) -> bool:
    return s is None or not str(s).strip()


def _sanitize_filename_component(s: str) -> str:
    """
    Make a reasonably safe filename component for Windows/macOS/Linux.
    Keeps letters/numbers/dot/dash/underscore; converts everything else to '_'.
    """

    s = (s or "").strip()
    if not s:
        return "data"

    # Replace any character outside the allowlist.
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s)
    # Avoid leading/trailing dots/spaces (Windows quirks).
    s = s.strip(" .")
    return s or "data"


def _default_output_path(args: argparse.Namespace) -> str:
    ticker = _sanitize_filename_component(str(args.ticker))
    interval = _sanitize_filename_component(str(args.interval))

    if not _is_empty_or_whitespace(args.start):
        start = _sanitize_filename_component(str(args.start))
        end = _sanitize_filename_component(str(args.end)) if not _is_empty_or_whitespace(args.end) else "today"
        span = f"{start}_to_{end}"
    else:
        span = _sanitize_filename_component(str(args.period))

    return f"{ticker}_{span}_{interval}.csv"


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="fetch_stock_timeseries.py",
        description="Download OHLCV time-series for a ticker over a date range or a period.",
    )

    p.add_argument(
        "--ticker",
        required=True,
        help="Ticker symbol, e.g. AAPL, MSFT, TSLA, RELIANCE.NS",
    )

    period_group = p.add_mutually_exclusive_group(required=True)
    period_group.add_argument(
        "--start",
        help="Start date (YYYY-MM-DD). Use with --end (optional).",
    )
    period_group.add_argument(
        "--period",
        help="Yahoo period string, e.g. 5d, 1mo, 3mo, 1y, 5y, max.",
    )

    p.add_argument(
        "--end",
        help="End date (YYYY-MM-DD). Only valid with --start.",
    )

    p.add_argument(
        "--interval",
        default="1d",
        help="Bar interval, e.g. 1m, 5m, 15m, 1h, 1d, 1wk, 1mo. Default: 1d",
    )

    p.add_argument(
        "--auto-adjust",
        action="store_true",
        help="Use adjusted prices (adjusts OHLC for splits/dividends).",
    )

    p.add_argument(
        "--prepost",
        action="store_true",
        help="Include pre/after-market data (when supported).",
    )

    p.add_argument(
        "--actions",
        action="store_true",
        help="Include dividends and stock splits columns (when available).",
    )

    p.add_argument(
        "--output",
        default=None,
        help="Output CSV path. If omitted, an auto-named CSV is written to the current directory.",
    )

    p.add_argument(
        "--stdout",
        action="store_true",
        help="Print CSV to stdout instead of writing a file.",
    )

    args = p.parse_args(argv)

    if not _is_empty_or_whitespace(args.end) and _is_empty_or_whitespace(args.start):
        p.error("--end can only be used with --start")

    return args


def _download(args: argparse.Namespace) -> pd.DataFrame:
    kwargs = dict(
        interval=args.interval,
        auto_adjust=bool(args.auto_adjust),
        prepost=bool(args.prepost),
        actions=bool(args.actions),
        progress=False,
        threads=True,
    )

    if not _is_empty_or_whitespace(args.start):
        df = yf.download(
            tickers=args.ticker,
            start=args.start,
            end=args.end,
            **kwargs,
        )
    else:
        df = yf.download(
            tickers=args.ticker,
            period=args.period,
            **kwargs,
        )

    # yfinance returns a MultiIndex on columns for multiple tickers; we only allow one ticker.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]  # type: ignore[assignment]

    return df


def main(argv: list[str]) -> int:
    args = _parse_args(argv)

    try:
        df = _download(args)
    except Exception as e:
        print(f"ERROR: download failed: {e}", file=sys.stderr)
        return 2

    if df is None or df.empty:
        today = date.today().isoformat()
        print(
            "ERROR: no data returned. Check ticker/market suffix, interval, and date range.\n"
            f"Hint: examples: AAPL, MSFT, RELIANCE.NS, 7203.T (Toyota), ^GSPC.\n"
            f"Today: {today}",
            file=sys.stderr,
        )
        return 3

    # Make the index explicit for CSV output.
    df = df.reset_index()

    if bool(args.stdout):
        df.to_csv(sys.stdout, index=False)
    else:
        output_path = args.output if not _is_empty_or_whitespace(args.output) else _default_output_path(args)
        df.to_csv(output_path, index=False)
        print(f"Wrote {len(df)} rows to {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

