import pytest
responses = pytest.importorskip("responses")

from pokemon.services.api import url, get_json
from pokemon.models import ApiResourceCache


@responses.activate
@pytest.mark.django_db
def test_real_http_layer_behaviour():
    u = url("pokemon", 25)

    # first request → 200 with validators, should create cache row
    responses.add(
        responses.GET, u,
        json={"id": 25, "name": "pikachu"},
        status=200,
        headers={"ETag": "abc", "Last-Modified": "lm"}
    )
    assert get_json(u) == {"id": 25, "name": "pikachu"}
    assert ApiResourceCache.objects.filter(url=u).exists()

    # second request → 304 Not Modified, should reuse cached payload
    responses.add(responses.GET, u, status=304)
    assert get_json(u) == {"id": 25, "name": "pikachu"}