import datetime as dt
import pytest

from pokemon.models import ApiResourceCache
from pokemon.services.api import url, get_json

from .conftest import FakeResponse


@pytest.mark.django_db
def test_extra_headers_are_merged_with_conditionals(freeze_now, patch_session):
    u = url("type")
    ApiResourceCache.objects.create(
        url=u,
        payload={"ok": True},
        etag="W/123",
        last_modified="lm",
        expires_at=freeze_now - dt.timedelta(seconds=1),  # stale
    )
    session = patch_session(FakeResponse(status_code=304))

    _ = get_json(u, extra_headers={"X-Trace-Id": "abc"})
    sent = session.calls[-1]["headers"]
    assert sent.get("If-None-Match") == "W/123"
    assert sent.get("If-Modified-Since") == "lm"
    assert sent.get("X-Trace-Id") == "abc"


@pytest.mark.django_db
def test_no_validators_sends_no_conditional_headers(freeze_now, patch_session):
    u = url("pokemon", 7)
    ApiResourceCache.objects.create(
        url=u, payload={"id": 7}, expires_at=freeze_now - dt.timedelta(seconds=1)
    )
    session = patch_session(FakeResponse(status_code=200, json_data={"id": 7}))

    _ = get_json(u)
    sent = session.calls[-1]["headers"]
    assert "If-None-Match" not in sent
    assert "If-Modified-Since" not in sent


@pytest.mark.django_db
def test_extra_headers_can_override_conditionals(freeze_now, patch_session):
    """
    Current behavior: extra headers `.update()` can override conditional ones.
    Adjust this test if you choose to forbid overrides in implementation.
    """
    u = url("type")
    ApiResourceCache.objects.create(
        url=u,
        payload={},
        etag="W/OVERRIDE-ME",
        last_modified="lm",
        expires_at=freeze_now - dt.timedelta(seconds=1),
    )
    session = patch_session(FakeResponse(status_code=304))

    _ = get_json(u, extra_headers={"If-None-Match": "OVERRIDE"})
    sent = session.calls[-1]["headers"]
    assert sent.get("If-None-Match") == "OVERRIDE"