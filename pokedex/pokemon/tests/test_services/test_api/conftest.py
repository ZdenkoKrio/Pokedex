"""
Common test helpers and fixtures for the API client unit tests.

Exposes:
- FakeResponse: minimal stand-in for `requests.Response` with configurable status/json/headers.
- FakeSession: captures GET calls and returns a preconfigured FakeResponse.
- freeze_now: freezes the cache layer's `_now()` for deterministic TTL math.
- patch_session: patches the API client's `get_session()` to return a FakeSession.
"""

from __future__ import annotations

import datetime as dt
from typing import Any, Dict, List, Optional

import pytest
from django.utils import timezone


class FakeResponse:
    """
    Minimal fake of `requests.Response` for unit tests.

    Parameters
    ----------
    status_code : int
        HTTP status code returned to the client.
    json_data : dict | None
        JSON payload returned by `.json()`. Defaults to {}.
    headers : dict | None
        Response headers. Useful for ETag / Last-Modified tests.
    raise_err : bool
        If True, `.raise_for_status()` raises AssertionError to simulate HTTP errors.
        (We intentionally use AssertionError so tests don't depend on requests' exact exceptions.)
    """

    def __init__(
        self,
        status_code: int = 200,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        raise_err: bool = False,
    ) -> None:
        self.status_code = status_code
        self._json: Dict[str, Any] = {} if json_data is None else json_data
        self.headers: Dict[str, str] = {} if headers is None else headers
        self._raise_err = raise_err

    def raise_for_status(self) -> None:
        """Simulate `requests.Response.raise_for_status()`."""
        if self._raise_err:
            raise AssertionError("HTTP error raised by FakeResponse")

    def json(self) -> Dict[str, Any]:
        """Return the configured JSON payload."""
        return self._json


class FakeSession:
    """
    Stand-in for a `requests.Session`.

    - Records every GET call (URL, timeout, headers) in `calls`.
    - Always returns the provided `FakeResponse`.
    """

    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.calls: List[Dict[str, Any]] = []

    def get(self, url: str, timeout: Optional[float] = None, headers: Optional[Dict[str, str]] = None) -> FakeResponse:
        self.calls.append({"url": url, "timeout": timeout, "headers": dict(headers or {})})
        return self.response


@pytest.fixture
def freeze_now(monkeypatch):
    """
    Freeze `pokemon.services.api.cache._now()` so TTL/expiry math is deterministic.

    Returns
    -------
    datetime
        The frozen aware datetime used by the cache layer.
    """
    frozen = timezone.make_aware(dt.datetime(2024, 1, 1, 12, 0, 0))
    # The cache layer imports `_now` from its own module.
    monkeypatch.setattr("pokemon.services.api.cache._now", lambda: frozen)
    return frozen


@pytest.fixture
def patch_session(monkeypatch):
    """
    Patch the API client's session factory to return a controlled FakeSession.

    This tries both import paths:
      - `pokemon.services.api.session.get_session`  (canonical)
      - `pokemon.services.api.client.get_session`   (if re-exported in client)

    Usage
    -----
    session = patch_session(FakeResponse(...))
    # Access `session.calls[-1]` to assert URL/headers/timeout were passed correctly.
    """

    def _factory(resp: FakeResponse) -> FakeSession:
        s = FakeSession(resp)
        # Patch the canonical location.
        try:
            monkeypatch.setattr("pokemon.services.api.session.get_session", lambda: s, raising=True)
        except Exception:
            pass
        # Patch potential re-export on client as a fallback.
        try:
            monkeypatch.setattr("pokemon.services.api.client.get_session", lambda: s, raising=True)
        except Exception:
            pass
        return s

    return _factory