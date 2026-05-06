"""Integration tests for the cross-tenant query guard.

The guard listens on SQLAlchemy `do_orm_execute` for SELECTs against models
with a direct `org_id` column. Without `org_id` in the WHERE clause it logs
a warning (`TENANCY_GUARD=warn`) or raises (`TENANCY_GUARD=strict`).
"""


import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from api.models import Base, Constraint, Event, Invitation, Organization, Person, Solution, Team
from api.utils.tenancy_guard import (
    TenancyViolationError,
    install_tenancy_guard,
)


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    install_tenancy_guard(Session)
    s = factory()
    org = Organization(id="t_org", name="T", region="T")
    person = Person(
        id="t_p",
        org_id="t_org",
        name="T P",
        email="tp@example.com",
        password_hash="$2b$12$x",
        roles=["volunteer"],
    )
    s.add_all([org, person])
    s.commit()
    yield s
    s.close()
    engine.dispose()


@pytest.fixture
def strict(monkeypatch):
    monkeypatch.setenv("TENANCY_GUARD", "strict")


@pytest.fixture
def warn(monkeypatch):
    monkeypatch.setenv("TENANCY_GUARD", "warn")


@pytest.fixture
def off(monkeypatch):
    monkeypatch.setenv("TENANCY_GUARD", "off")


@pytest.mark.parametrize("model", [Person, Team, Event, Constraint, Solution, Invitation])
def test_strict_raises_when_org_id_filter_is_missing(session, strict, model):
    with pytest.raises(TenancyViolationError):
        session.query(model).all()


@pytest.mark.parametrize("model", [Person, Team, Event, Constraint, Solution, Invitation])
def test_strict_passes_when_org_id_filter_present(session, strict, model):
    # Should not raise — exact rows don't matter, only that the listener allows it.
    list(session.query(model).filter(model.org_id == "t_org").all())


def test_warn_does_not_raise(session, warn, caplog):
    """Warn mode logs but the query proceeds."""
    import logging

    with caplog.at_level(logging.WARNING):
        rows = session.query(Person).all()
    assert isinstance(rows, list)
    assert any("Tenancy guard" in r.message for r in caplog.records)


def test_off_disables_the_guard(session, off):
    rows = session.query(Person).all()
    assert isinstance(rows, list)


def test_organization_query_is_not_guarded(session, strict):
    """Organization itself has no org_id — it's the tenant root."""
    list(session.query(Organization).all())


def test_count_with_org_id_filter_is_allowed(session, strict):
    session.query(Person).filter(Person.org_id == "t_org").count()


def test_first_with_org_id_filter_is_allowed(session, strict):
    session.query(Person).filter(Person.org_id == "t_org").first()


def test_join_with_org_id_filter_on_parent_passes(session, strict):
    """Joining Assignment to Event and filtering Event.org_id should pass."""
    # Assignment has no org_id, but Event does. The query has org_id in WHERE
    # via the Event join.
    from api.models import Assignment

    list(
        session.query(Assignment)
        .join(Event, Assignment.event_id == Event.id)
        .filter(Event.org_id == "t_org")
        .all()
    )
