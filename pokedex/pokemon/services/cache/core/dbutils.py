from __future__ import annotations
from typing import Sequence, Set, Any
from django.db.models import Model, QuerySet


def db_have_values(model: type[Model], field_name: str, values: Sequence[Any]) -> Set[Any]:  # noqa: ANN401
    """
    Return subset of `values` already present in DB for `model.field_name`.
    """
    if not values:
        return set()
    qs: QuerySet = model.objects.filter(**{f"{field_name}__in": values}).values_list(field_name, flat=True)
    return set(qs)


def missing_after_chunk(model: type[Model], field_name: str, chunk: Sequence[Any]) -> Set[Any]:  # noqa: ANN401
    """
    Compute which values from `chunk` are still missing for `model.field_name`.
    """
    return set(chunk) - db_have_values(model, field_name, chunk)