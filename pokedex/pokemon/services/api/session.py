from __future__ import annotations

import threading
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_tls = threading.local()


def get_session() -> requests.Session:
    """
    Return a thread-local `requests.Session` configured with:
    - Connection pooling (shared adapters for http/https).
    - Conservative retries for common transient errors.

    Notes
    -----
    `allowed_methods` must be an iterable of uppercased methods for urllib3.
    """
    s = getattr(_tls, "session", None)

    if s is None:
        s = requests.Session()

        retry = Retry(
            total=3,
            backoff_factor=0.2,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET", "HEAD"}),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=50, pool_maxsize=50)
        s.mount("https://", adapter)
        s.mount("http://", adapter)

        _tls.session = s
    return s