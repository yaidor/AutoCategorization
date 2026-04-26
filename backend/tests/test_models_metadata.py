from app.db.base import Base
from app.models import Categorization, Customer, Meeting, Seller


def test_all_tables_registered() -> None:
    table_names = set(Base.metadata.tables.keys())
    assert table_names == {"sellers", "customers", "meetings", "categorizations"}


def test_models_have_expected_tablenames() -> None:
    assert Seller.__tablename__ == "sellers"
    assert Customer.__tablename__ == "customers"
    assert Meeting.__tablename__ == "meetings"
    assert Categorization.__tablename__ == "categorizations"


def test_meeting_indexes_are_present() -> None:
    indexes = {idx.name for idx in Meeting.__table__.indexes}
    assert "ix_meetings_seller_date" in indexes
    assert "ix_meetings_closed" in indexes


def test_categorization_unique_constraint_on_meeting_prompt_model() -> None:
    constraints = {c.name for c in Categorization.__table__.constraints}
    assert "uq_categorizations_meeting_prompt_model" in constraints


def test_categorization_gin_index_on_key_topics() -> None:
    indexes = {idx.name: idx.dialect_options for idx in Categorization.__table__.indexes}
    assert indexes["ix_categorizations_key_topics"]["postgresql"]["using"] == "gin"
