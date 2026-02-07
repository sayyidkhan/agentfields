# Stock time-series downloader (Python)

Downloads OHLCV time-series data for **any stock ticker** over a **given time period** using Yahoo Finance via `yfinance` (no API key required).

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Examples

### Date range (recommended)

```powershell
python fetch_stock_timeseries.py --ticker AAPL --start 2024-01-01 --end 2024-12-31 --interval 1d --output aapl_2024.csv
```

### Period string

```powershell
python fetch_stock_timeseries.py --ticker MSFT --period 6mo --interval 1d --output msft_6mo.csv
```

### Intraday (last few days)

```powershell
python fetch_stock_timeseries.py --ticker TSLA --period 5d --interval 5m --output tsla_5d_5m.csv
```

### Auto-named output file (no `--output`)

```powershell
python fetch_stock_timeseries.py --ticker "^GSPC" --period 1mo --interval 1d
```

### Print CSV to stdout

```powershell
python fetch_stock_timeseries.py --ticker "^GSPC" --period 1mo --interval 1d --stdout
```

## Notes

- Tickers can require exchange suffixes depending on market, e.g.:
  - `RELIANCE.NS` (NSE India)
  - `7203.T` (Tokyo)
- If you get “no data returned”, try a different `--interval` or confirm the ticker symbol/suffix.

