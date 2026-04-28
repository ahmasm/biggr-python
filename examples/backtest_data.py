"""Pull multi-year quarterly fundamentals into a pandas DataFrame.

biggr itself doesn't depend on pandas — install it separately:
    pip install pandas
"""

import pandas as pd

from biggr import Client


def main() -> None:
    c = Client()
    rows = c.financials.income(
        "MSFT",
        period="quarterly",
        format="standardized",
        type="point_in_time",
    )

    df = pd.DataFrame(rows)
    if "filing_date" in df.columns:
        df["filing_date"] = pd.to_datetime(df["filing_date"], errors="coerce")
        df = df.sort_values("filing_date")

    cols = [
        c
        for c in ["fiscal_period", "filing_date", "Revenue", "Net_Income", "EPS_Basic"]
        if c in df.columns
    ]
    print(df[cols].tail(12).to_string(index=False))


if __name__ == "__main__":
    main()
