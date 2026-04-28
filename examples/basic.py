"""Fetch AAPL quarterly income statement (no API key needed)."""

from biggr import Client


def main() -> None:
    c = Client()  # trial mode — AAPL is in the trial ticker list
    rows = c.financials.income(
        "AAPL",
        period="quarterly",
        format="standardized",
        type="point_in_time",
        limit=4,
    )

    print(f"AAPL — {len(rows)} most recent quarters (point-in-time)\n")
    for r in rows:
        revenue = r.get("Revenue") or r.get("revenue")
        net_income = r.get("Net_Income") or r.get("net_income")
        print(
            f"  {r['fiscal_period']:8} "
            f"filed {r.get('filing_date', '?'):10} "
            f"revenue={revenue:>15} "
            f"net_income={net_income:>15}"
        )


if __name__ == "__main__":
    main()
