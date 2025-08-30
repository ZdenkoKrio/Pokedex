# pokemon/tests/services/api/test_errors.py
import pytest
import requests
from pokemon.services.api import url, get_json
from pokemon.models import ApiResourceCache
from .conftest import FakeResponse, FakeSession

@pytest.mark.django_db
def test_http_5xx_raises(patch_session):
    u = url("type")
    ApiResourceCache.objects.filter(url=u).delete()  # vynúť HTTP
    patch_session(FakeResponse(status_code=500, raise_err=True))
    with pytest.raises(AssertionError):
        get_json(u)

class BadJsonResponse(FakeResponse):
    def json(self):
        raise ValueError("bad json")

@pytest.mark.django_db
def test_bad_json_bubbles_up(patch_session):
    u = url("type")
    ApiResourceCache.objects.filter(url=u).delete()
    patch_session(BadJsonResponse(status_code=200))
    with pytest.raises(ValueError):
        get_json(u)

class TimeoutSession(FakeSession):
    def get(self, *a, **kw):
        raise requests.Timeout("boom")

@pytest.mark.django_db
def test_timeout_propagates(monkeypatch):
    u = url("type")
    ApiResourceCache.objects.filter(url=u).delete()
    # patchni obe cesty pre istotu
    try:
        monkeypatch.setattr("pokemon.services.api.session.get_session",
                            lambda: TimeoutSession(FakeResponse()))
    except Exception:
        pass
    try:
        monkeypatch.setattr("pokemon.services.api.client.get_session",
                            lambda: TimeoutSession(FakeResponse()))
    except Exception:
        pass
    with pytest.raises(requests.Timeout):
        get_json(u, timeout=0.001)