"""Compare point-in-time and restated values for the same fiscal period.

Most APIs silently overwrite history with restated numbers. biggr keeps
both versions so backtests don't accidentally see future restatements.
"""

from biggr import Client


def main() -> None:
    c = Client()
    ticker = "AAPL"

    pit = c.financials.income(ticker, period="yearly", type="point_in_time")
    restated = c.financials.income(ticker, period="yearly", type="restated")

    pit_by_period = {r["fiscal_period"]: r for r in pit}
    restated_by_period = {r["fiscal_period"]: r for r in restated}

    shared = sorted(set(pit_by_period) & set(restated_by_period), reverse=True)

    print(f"{ticker} — Revenue: PIT vs Restated\n")
    print(f"  {'period':8} {'pit':>18} {'restated':>18} {'delta':>15}")
    print(f"  {'-' * 8} {'-' * 18:>18} {'-' * 18:>18} {'-' * 15:>15}")

    for period in shared[:10]:
        pit_rev = pit_by_period[period].get("Revenue") or 0
        rest_rev = restated_by_period[period].get("Revenue") or 0
        delta = rest_rev - pit_rev
        flag = "  <-- restated" if delta else ""
        print(f"  {period:8} {pit_rev:>18,} {rest_rev:>18,} {delta:>15,}{flag}")


if __name__ == "__main__":
    main()
