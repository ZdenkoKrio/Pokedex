import datetime as dt
import pytest
from pokemon.models import ApiResourceCache
from pokemon.services.api import url, get_json
from .conftest import FakeResponse


@pytest.mark.django_db
def test_cache_miss_creates_row(freeze_now, patch_session):
    u = url("pokemon", 10)
    session = patch_session(FakeResponse(
        status_code=200,
        json_data={"id": 10},
        headers={"ETag": "w/10", "Last-Modified": "lm"},
    ))
    data = get_json(u)
    assert data == {"id": 10}

    row = ApiResourceCache.objects.get(url=u)
    assert row.payload == {"id": 10}
    assert row.etag == "w/10"
    assert row.last_modified == "lm"
    assert session.calls[-1]["url"] == u


@pytest.mark.django_db
def test_returns_fresh_cache_without_http(freeze_now, patch_session):
    u = url("pokemon", 1)
    ApiResourceCache.objects.create(
        url=u,
        payload={"id": 1},
        etag="W/etag",
        last_modified="Mon, 01 Jan 2024 00:00:00 GMT",
        expires_at=freeze_now + dt.timedelta(hours=1),  # fresh
    )

    session = patch_session(FakeResponse(status_code=200, json_data={"id": 999}))
    data = get_json(u)
    assert data == {"id": 1}, "Should return fresh cached payload"
    assert session.calls == [], "No HTTP call expected when cache is fresh"