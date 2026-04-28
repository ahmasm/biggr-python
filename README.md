# biggr-python

Python client for [biggr](https://api-biggr.com) — US fundamentals API with as-reported + standardized data, point-in-time and restated columns separated, every value linked back to the source filing row.

## Install

```bash
pip install git+https://github.com/ahmasm/biggr-python
```

Requires Python 3.8+.

## Quick start (no API key)

The trial endpoints are public for a fixed list of tickers — no signup needed:

```python
from biggr import Client

c = Client()
income = c.financials.income("AAPL", period="quarterly", type="point_in_time")
print(income[0]["fiscal_period"], income[0]["filing_date"])
```

Trial tickers cover one company per industry template:

| Template | Tickers |
| --- | --- |
| General / tech | `AAPL`, `NVDA`, `MSFT`, `AMZN`, `META`, `TSLA` |
| Bank | `JPM` |
| Insurance | `PGR` |
| REIT | `O` |
| Utility | `NEE` |
| Broker | `SCHW` |

## Full access

Get an API key at [api-biggr.com](https://api-biggr.com). Pricing on the site.

```python
from biggr import Client

c = Client(api_key="bgr_live_...")          # or set BIGGR_API_KEY env var
balance = c.financials.balance_sheet("GOOG", period="yearly", format="as_reported")
```

Full access covers 4,200+ US-listed companies with multi-decade history.

## What's in the box

New 10-K / 10-Q / 8-K earnings filings are normalized and live in the API within ~10 minutes of SEC publication. Earnings data often hits via 8-K before the full 10-Q is filed weeks later.

```python
c.financials.income(ticker, **params)         # GET /v1/financials/{ticker}/income
c.financials.balance_sheet(ticker, **params)  # GET /v1/financials/{ticker}/balance-sheet
c.financials.cash_flow(ticker, **params)      # GET /v1/financials/{ticker}/cash-flow

c.prices.quote(ticker)                        # GET /v1/prices/{ticker}/quote
c.prices.bulk_quotes([t1, t2, ...])           # GET /v1/prices/quotes?symbols=...
c.prices.historical(ticker, timeframe="1Y")   # GET /v1/prices/{ticker}/historical

c.estimates.get(ticker)                       # GET /v1/estimates/{ticker}

c.news.get(ticker, from_="2025-01-01", to="2025-06-30")  # GET /v1/news/{ticker}
```

### Financials query params

| Param | Values | Default |
| --- | --- | --- |
| `period` | `quarterly`, `yearly` | `yearly` |
| `format` | `standardized`, `as_reported` | `standardized` |
| `type` | `restated`, `point_in_time` | `restated` |
| `screenshots` | `True`, `False` | `False` |
| `fiscal_period` | e.g. `2024`, `2024-Q3` | — |
| `start_date` | `YYYY-MM-DD` | — |
| `end_date` | `YYYY-MM-DD` | — |
| `limit` | int | — |

## Errors

```python
from biggr import Client, BiggrError, AuthenticationError, TrialRestrictedError

c = Client()
try:
    c.financials.income("GOOG")  # not in trial list
except TrialRestrictedError as e:
    print(e.status_code, e.message)
```

Exception classes: `BiggrError`, `AuthenticationError`, `TrialRestrictedError`, `NotFoundError`, `RateLimitError`.

## Examples

See [`examples/`](examples/):

- [`basic.py`](examples/basic.py) — fetch AAPL income statement
- [`backtest_data.py`](examples/backtest_data.py) — pull 10 years and load into a pandas DataFrame

## Roadmap

Near term:

- OTC tickers (over-the-counter US listings)
- ADRs / foreign filings (6-K, 20-F, 40-F)
- Ratios endpoint (currently you compute from raw line items)
- KPIs endpoint (company-specific operating metrics)
- MCP server (Model Context Protocol — query biggr from Claude/Cursor)

Longer term:

- International coverage: Japan, UK, Europe, India

## License

MIT — see [LICENSE](LICENSE).
