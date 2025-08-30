import datetime as dt
import pytest

from pokemon.models import ApiResourceCache
from pokemon.services.api import url, get_json

from .conftest import FakeResponse


@pytest.mark.django_db
def test_revalidate_304_bumps_expiry_and_returns_cached(freeze_now, patch_session):
    u = url("pokemon", 2)
    row = ApiResourceCache.objects.create(
        url=u,
        payload={"id": 2, "name": "old"},
        etag="etag-1",
        last_modified="Mon, 01 Jan 2024 00:00:00 GMT",
        expires_at=freeze_now - dt.timedelta(seconds=1),
    )
    session = patch_session(FakeResponse(
        status_code=304,  # Not Modified
        headers={"ETag": "etag-1", "Last-Modified": "Mon, 01 Jan 2024 00:00:00 GMT"},
    ))

    data = get_json(u, ttl=dt.timedelta(hours=6))
    assert data == {"id": 2, "name": "old"}

    row.refresh_from_db()
    assert row.expires_at == freeze_now + dt.timedelta(hours=6), "TTL must extend on 304"

    sent = session.calls[-1]["headers"]
    assert sent.get("If-None-Match") == "etag-1"
    assert sent.get("If-Modified-Since") == "Mon, 01 Jan 2024 00:00:00 GMT"


@pytest.mark.django_db
def test_revalidate_200_updates_payload_and_validators(freeze_now, patch_session):
    u = url("pokemon", 3)
    ApiResourceCache.objects.create(
        url=u,
        payload={"id": 3, "name": "old"},
        etag="etag-old",
        last_modified="old-lm",
        expires_at=freeze_now - dt.timedelta(seconds=1),
    )
    session = patch_session(FakeResponse(
        status_code=200,
        json_data={"id": 3, "name": "new"},
        headers={"ETag": "etag-new", "Last-Modified": "Tue, 02 Jan 2024 00:00:00 GMT"},
    ))

    data = get_json(u, ttl=dt.timedelta(hours=12))
    assert data == {"id": 3, "name": "new"}

    row = ApiResourceCache.objects.get(url=u)
    assert row.payload == {"id": 3, "name": "new"}
    assert row.etag == "etag-new"
    assert row.last_modified == "Tue, 02 Jan 2024 00:00:00 GMT"
    assert row.expires_at == freeze_now + dt.timedelta(hours=12)

    sent = session.calls[-1]["headers"]
    assert sent.get("If-None-Match") == "etag-old"
    assert sent.get("If-Modified-Since") == "old-lm"