from datetime import date

from sqlalchemy import select

from app.models import Categorization, Meeting
from app.services.metrics import MetricsFilters, _apply_filters


def _compile(stmt) -> str:
    return str(stmt.compile(compile_kwargs={"literal_binds": True}))


def _base_stmt():
    return select(Categorization).join(Meeting, Meeting.id == Categorization.meeting_id)


def test_empty_filters_adds_no_where_clauses() -> None:
    sql = _compile(_apply_filters(_base_stmt(), MetricsFilters()))
    assert "WHERE" not in sql.upper().split("FROM")[1]


def test_from_date_filter_adds_lower_bound() -> None:
    sql = _compile(_apply_filters(_base_stmt(), MetricsFilters(from_date=date(2024, 1, 1))))
    assert "meeting_date >=" in sql
    assert "2024-01-01" in sql


def test_to_date_filter_adds_upper_bound() -> None:
    sql = _compile(_apply_filters(_base_stmt(), MetricsFilters(to_date=date(2024, 12, 31))))
    assert "meeting_date <=" in sql
    assert "2024-12-31" in sql


def test_seller_id_filter_targets_meetings() -> None:
    sql = _compile(_apply_filters(_base_stmt(), MetricsFilters(seller_id=3)))
    assert "seller_id" in sql
    assert "3" in sql


def test_industry_filter_targets_categorizations() -> None:
    sql = _compile(
        _apply_filters(_base_stmt(), MetricsFilters(industry="saas_tech"))  # type: ignore[arg-type]
    )
    assert "industry" in sql.lower()


def test_closed_true_filter_uses_is_true() -> None:
    sql = _compile(_apply_filters(_base_stmt(), MetricsFilters(closed=True)))
    assert "closed IS true" in sql or "closed IS TRUE" in sql


def test_closed_false_filter_uses_is_false() -> None:
    sql = _compile(_apply_filters(_base_stmt(), MetricsFilters(closed=False)))
    assert "closed IS false" in sql or "closed IS FALSE" in sql


def test_combined_filters_all_applied() -> None:
    filters = MetricsFilters(
        from_date=date(2024, 1, 1),
        to_date=date(2024, 12, 31),
        seller_id=2,
        closed=True,
    )
    sql = _compile(_apply_filters(_base_stmt(), filters))
    assert "meeting_date >=" in sql
    assert "meeting_date <=" in sql
    assert "seller_id" in sql
    assert "closed" in sql.lower()


def test_filters_dataclass_is_frozen() -> None:
    import pytest

    f = MetricsFilters(seller_id=1)
    with pytest.raises((AttributeError, Exception)):
        f.seller_id = 2  # type: ignore[misc]
