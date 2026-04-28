"""
biggr — Python client for the biggr SEC financials API.

Trial mode (no API key): AAPL, NVDA, MSFT, AMZN, META, TSLA, JPM, PGR, O, NEE, SCHW
Full access (with API key): 4,200+ US-listed companies.

    from biggr import Client

    c = Client()                              # trial mode
    income = c.financials.income("AAPL", period="quarterly", type="point_in_time")

    c = Client(api_key="bgr_live_...")        # full access
    bs = c.financials.balance_sheet("GOOG", period="yearly", format="as_reported")
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests


__version__ = "0.1.0"
DEFAULT_BASE_URL = "https://thebiggr.com"
DEFAULT_TIMEOUT = 30.0


class BiggrError(Exception):
    def __init__(self, status_code: int, message: str, payload: Optional[Any] = None):
        super().__init__(f"{status_code}: {message}")
        self.status_code = status_code
        self.message = message
        self.payload = payload


class AuthenticationError(BiggrError):
    pass


class TrialRestrictedError(BiggrError):
    """Raised when a trial-mode call hits a non-trial ticker."""


class NotFoundError(BiggrError):
    pass


class RateLimitError(BiggrError):
    pass


class Client:
    """biggr API client.

    If ``api_key`` is omitted (and no ``BIGGR_API_KEY`` env var is set), the
    client routes calls to the public trial endpoints, which support a
    fixed list of tickers without authentication.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        session: Optional[requests.Session] = None,
    ):
        self.api_key = api_key if api_key is not None else os.getenv("BIGGR_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = session or requests.Session()
        self._is_trial = self.api_key is None

        self.financials = _Financials(self)
        self.prices = _Prices(self)
        self.estimates = _Estimates(self)
        self.news = _News(self)

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{path}"
        headers = {"User-Agent": f"biggr-python/{__version__}"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        cleaned = (
            {k: _format_param(v) for k, v in params.items() if v is not None}
            if params
            else None
        )

        resp = self._session.get(
            url, headers=headers, params=cleaned, timeout=self.timeout
        )
        return self._parse(resp)

    @staticmethod
    def _parse(resp: requests.Response) -> Any:
        if 200 <= resp.status_code < 300:
            try:
                return resp.json()
            except ValueError:
                return resp.text

        try:
            payload = resp.json()
            message = payload.get("message") if isinstance(payload, dict) else str(payload)
            error_code = payload.get("error") if isinstance(payload, dict) else None
        except ValueError:
            payload = resp.text
            message = resp.text or resp.reason
            error_code = None

        if resp.status_code == 401:
            raise AuthenticationError(401, message or "Authentication failed", payload)
        if resp.status_code == 403 and (
            error_code == "trial_restricted"
            or (isinstance(message, str) and "Trial access is limited" in message)
        ):
            raise TrialRestrictedError(403, message or "Trial restricted", payload)
        if resp.status_code == 404:
            raise NotFoundError(404, message or "Not found", payload)
        if resp.status_code == 429:
            raise RateLimitError(429, message or "Rate limited", payload)
        raise BiggrError(resp.status_code, message or "Request failed", payload)


def _format_param(value: Any) -> Any:
    if isinstance(value, bool):
        return "true" if value else "false"
    return value


class _Financials:
    def __init__(self, client: Client):
        self._c = client

    def income(self, ticker: str, **params) -> List[Dict[str, Any]]:
        return self._statement(ticker, "income", params)

    def balance_sheet(self, ticker: str, **params) -> List[Dict[str, Any]]:
        return self._statement(ticker, "balance-sheet", params)

    def cash_flow(self, ticker: str, **params) -> List[Dict[str, Any]]:
        return self._statement(ticker, "cash-flow", params)

    def _statement(self, ticker: str, kind: str, params: Dict[str, Any]):
        prefix = "/v1/trial" if self._c._is_trial else "/v1/financials"
        return self._c._get(f"{prefix}/{ticker.upper()}/{kind}", params)


class _Prices:
    def __init__(self, client: Client):
        self._c = client

    def quote(self, ticker: str) -> Dict[str, Any]:
        prefix = "/v1/trial" if self._c._is_trial else "/v1/prices"
        return self._c._get(f"{prefix}/{ticker.upper()}/quote")

    def bulk_quotes(self, symbols: List[str]) -> List[Dict[str, Any]]:
        prefix = "/v1/trial" if self._c._is_trial else "/v1/prices"
        joined = ",".join(s.upper() for s in symbols)
        return self._c._get(f"{prefix}/quotes", {"symbols": joined})

    def historical(self, ticker: str, timeframe: str = "1Y") -> List[Dict[str, Any]]:
        prefix = "/v1/trial" if self._c._is_trial else "/v1/prices"
        return self._c._get(
            f"{prefix}/{ticker.upper()}/historical", {"timeframe": timeframe}
        )


class _Estimates:
    def __init__(self, client: Client):
        self._c = client

    def get(self, ticker: str) -> Any:
        if self._c._is_trial:
            return self._c._get(f"/v1/trial/{ticker.upper()}/estimates")
        return self._c._get(f"/v1/estimates/{ticker.upper()}")


class _News:
    def __init__(self, client: Client):
        self._c = client

    def get(
        self,
        ticker: str,
        from_: Optional[str] = None,
        to: Optional[str] = None,
    ) -> Any:
        params = {"from": from_, "to": to}
        if self._c._is_trial:
            return self._c._get(f"/v1/trial/{ticker.upper()}/news", params)
        return self._c._get(f"/v1/news/{ticker.upper()}", params)


__all__ = [
    "Client",
    "BiggrError",
    "AuthenticationError",
    "TrialRestrictedError",
    "NotFoundError",
    "RateLimitError",
    "__version__",
]
