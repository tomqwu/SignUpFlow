"""Atomic allocation changes across independent database connections."""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.models import (
    Assignment,
    AuditAction,
    AuditLog,
    Availability,
    Base,
    Event,
    Notification,
    Organization,
    Person,
    Solution,
    VacationPeriod,
)
from api.services.allocation_service import (
    AllocationConflictError,
    claim_open_shift,
    cover_swap,
)
from api.services.publication_service import (
    PublicationConflictError,
    capture_solution_scope,
    publish_solution_transaction,
)
from api.timeutils import utcnow


def _database_url(tmp_path) -> str:
    return os.getenv(
        "SIGNUPFLOW_CONCURRENCY_DATABASE_URL",
        f"sqlite:///{tmp_path / 'assignment-claims.db'}",
    )


@pytest.fixture
def claim_database(tmp_path):
    url = _database_url(tmp_path)
    connect_args = {"check_same_thread": False, "timeout": 10} if url.startswith("sqlite") else {}
    engine = create_engine(url, connect_args=connect_args, pool_pre_ping=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    try:
        yield factory
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


def _seed(
    factory,
    *,
    org_id: str,
    people: dict[str, list[str]],
    events: dict[str, tuple[int, dict[str, int]]],
) -> None:
    start = utcnow() + timedelta(days=30)
    with factory() as db:
        db.add(Organization(id=org_id, name=org_id))
        for person_id, roles in people.items():
            db.add(
                Person(
                    id=person_id,
                    org_id=org_id,
                    name=person_id,
                    email=f"{person_id}@example.test",
                    roles=roles,
                    status="active",
                )
            )
        for event_id, (minute_offset, role_counts) in events.items():
            event_start = start + timedelta(minutes=minute_offset)
            db.add(
                Event(
                    id=event_id,
                    org_id=org_id,
                    type=event_id,
                    start_time=event_start,
                    end_time=event_start + timedelta(hours=1),
                    extra_data={"role_counts": role_counts},
                )
            )
        db.commit()


def _claim(factory, barrier: Barrier, org_id: str, event_id: str, person_id: str, role: str):
    with factory() as db:
        barrier.wait()
        try:
            assignment, changed = claim_open_shift(
                db,
                org_id=org_id,
                event_id=event_id,
                person_id=person_id,
                role=role,
                actor_email=f"{person_id}@example.test",
            )
            db.commit()
            return "won", assignment.id, changed
        except AllocationConflictError as exc:
            db.rollback()
            return exc.code, None, False


def _scoped_solution(factory, *, org_id: str, person_id: str, event_id: str) -> int:
    with factory() as db:
        event = db.query(Event).filter(Event.org_id == org_id, Event.id == event_id).one()
        scope = capture_solution_scope(
            [event],
            range_start=event.start_time.date(),
            range_end=event.start_time.date(),
        )
        solution = Solution(
            org_id=org_id,
            hard_violations=0,
            soft_score=0.0,
            health_score=100.0,
            scope_start=scope.range_start,
            scope_end=scope.range_end,
            scope_event_ids=scope.event_ids,
            scope_fingerprint=scope.fingerprint,
        )
        db.add(solution)
        db.flush()
        db.add(
            Assignment(
                solution_id=solution.id,
                event_id=event_id,
                person_id=person_id,
                role="usher",
            )
        )
        db.commit()
        return solution.id


def _publish(
    factory,
    barrier: Barrier | None,
    *,
    org_id: str,
    solution_id: int,
    action: str = AuditAction.SOLUTION_PUBLISHED,
    rollback: bool = False,
) -> str:
    with factory() as db:
        actor = db.query(Person).filter(Person.org_id == org_id, Person.id == "admin").one()
        if barrier is not None:
            barrier.wait()
        try:
            publish_solution_transaction(
                db,
                solution_id=solution_id,
                org_id=org_id,
                actor=actor,
                action=action,
                require_previously_published=rollback,
            )
            db.commit()
            return "published"
        except PublicationConflictError:
            db.rollback()
            return "rejected"


@pytest.mark.integration
def test_two_people_claiming_last_slot_have_one_winner(claim_database):
    factory = claim_database
    _seed(
        factory,
        org_id="claim-one-slot",
        people={
            "first": ["volunteer", "usher"],
            "second": ["volunteer", "usher"],
        },
        events={"service": (0, {"usher": 1})},
    )

    barrier = Barrier(2, timeout=10)
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(
            executor.map(
                lambda person_id: _claim(
                    factory, barrier, "claim-one-slot", "service", person_id, "usher"
                ),
                ("first", "second"),
            )
        )

    assert sorted(result[0] for result in results) == ["role_full", "won"]
    with factory() as db:
        rows = (
            db.query(Assignment)
            .join(Event, Assignment.event_id == Event.id)
            .filter(Event.org_id == "claim-one-slot", Assignment.event_id == "service")
            .all()
        )
        assert len(rows) == 1
        assert rows[0].response_current is True
        assert db.query(AuditLog).filter(AuditLog.organization_id == "claim-one-slot").count() == 1
        assert db.query(Notification).filter(Notification.org_id == "claim-one-slot").count() == 0


@pytest.mark.integration
def test_concurrent_overlapping_claims_allow_at_most_one(claim_database):
    factory = claim_database
    _seed(
        factory,
        org_id="claim-overlap",
        people={"member": ["volunteer", "usher"]},
        events={
            "early": (0, {"usher": 1}),
            "overlap": (30, {"usher": 1}),
        },
    )

    barrier = Barrier(2, timeout=10)
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(
            executor.map(
                lambda event_id: _claim(
                    factory, barrier, "claim-overlap", event_id, "member", "usher"
                ),
                ("early", "overlap"),
            )
        )

    assert sorted(result[0] for result in results) == ["overlap", "won"]
    with factory() as db:
        rows = (
            db.query(Assignment)
            .join(Event, Assignment.event_id == Event.id)
            .filter(Event.org_id == "claim-overlap", Assignment.person_id == "member")
            .all()
        )
        assert len(rows) == 1


@pytest.mark.integration
def test_adjacent_non_overlapping_claims_remain_allowed(claim_database):
    factory = claim_database
    _seed(
        factory,
        org_id="claim-adjacent",
        people={"member": ["volunteer", "usher"]},
        events={
            "first": (0, {"usher": 1}),
            "second": (60, {"usher": 1}),
        },
    )

    for event_id in ("first", "second"):
        with factory() as db:
            _, changed = claim_open_shift(
                db,
                org_id="claim-adjacent",
                event_id=event_id,
                person_id="member",
                role="usher",
                actor_email="member@example.test",
            )
            db.commit()
            assert changed is True


@pytest.mark.integration
def test_swap_cover_has_one_winner_and_winner_retry_is_idempotent(claim_database):
    factory = claim_database
    _seed(
        factory,
        org_id="swap-race",
        people={
            "owner": ["volunteer", "usher"],
            "first": ["volunteer", "usher"],
            "second": ["volunteer", "usher"],
        },
        events={"service": (0, {"usher": 1})},
    )
    with factory() as db:
        swap = Assignment(
            event_id="service",
            person_id="owner",
            role="usher",
            status="swap_requested",
            response_status="declined",
            commitment_revision=1,
            response_revision=1,
            responded_by_person_id="owner",
        )
        db.add(swap)
        db.commit()
        swap_id = swap.id

    barrier = Barrier(2, timeout=10)

    def attempt(person_id: str):
        with factory() as db:
            barrier.wait()
            try:
                assignment, changed = cover_swap(
                    db,
                    org_id="swap-race",
                    assignment_id=swap_id,
                    person_id=person_id,
                    actor_email=f"{person_id}@example.test",
                )
                db.commit()
                return "won", assignment.person_id, changed
            except AllocationConflictError as exc:
                db.rollback()
                return exc.code, None, False

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(attempt, ("first", "second")))

    winner = next(result[1] for result in results if result[0] == "won")
    assert sorted(result[0] for result in results) == ["swap_unavailable", "won"]

    with factory() as db:
        assignment, changed = cover_swap(
            db,
            org_id="swap-race",
            assignment_id=swap_id,
            person_id=winner,
            actor_email=f"{winner}@example.test",
        )
        db.commit()
        assert changed is False
        assert assignment.person_id == winner
        assert db.query(AuditLog).filter(AuditLog.organization_id == "swap-race").count() == 1


@pytest.mark.integration
def test_claim_revalidates_qualification_availability_and_rolls_back_audit_failure(
    claim_database,
):
    factory = claim_database
    _seed(
        factory,
        org_id="claim-validation",
        people={
            "unqualified": ["volunteer"],
            "away": ["volunteer", "usher"],
            "eligible": ["volunteer", "usher"],
        },
        events={"service": (0, {"usher": 1})},
    )
    with factory() as db:
        event = db.query(Event).filter(Event.id == "service").one()
        availability = Availability(person_id="away")
        db.add(availability)
        db.flush()
        db.add(
            VacationPeriod(
                availability_id=availability.id,
                start_date=event.start_time.date(),
                end_date=event.start_time.date(),
            )
        )
        db.commit()

    for person_id, expected_code in (
        ("unqualified", "not_qualified"),
        ("away", "unavailable"),
    ):
        with factory() as db:
            with pytest.raises(AllocationConflictError, match=expected_code):
                claim_open_shift(
                    db,
                    org_id="claim-validation",
                    event_id="service",
                    person_id=person_id,
                    role="usher",
                    actor_email=f"{person_id}@example.test",
                )
            db.rollback()

    with factory() as db:
        with patch(
            "api.services.allocation_service.log_audit_event",
            side_effect=RuntimeError("audit unavailable"),
        ):
            with pytest.raises(RuntimeError, match="audit unavailable"):
                claim_open_shift(
                    db,
                    org_id="claim-validation",
                    event_id="service",
                    person_id="eligible",
                    role="usher",
                    actor_email="eligible@example.test",
                )
                db.commit()
        db.rollback()

    with factory() as db:
        assert (
            db.query(Assignment)
            .join(Event, Assignment.event_id == Event.id)
            .filter(Event.org_id == "claim-validation")
            .count()
            == 0
        )
        assert (
            db.query(AuditLog).filter(AuditLog.organization_id == "claim-validation").count() == 0
        )


@pytest.mark.integration
def test_draft_solution_history_does_not_consume_live_capacity(claim_database):
    factory = claim_database
    _seed(
        factory,
        org_id="claim-draft-history",
        people={
            "draft-member": ["volunteer", "usher"],
            "live-member": ["volunteer", "usher"],
        },
        events={"service": (0, {"usher": 1})},
    )
    with factory() as db:
        solution = Solution(
            org_id="claim-draft-history",
            hard_violations=0,
            soft_score=0.0,
            health_score=100.0,
            is_published=False,
        )
        db.add(solution)
        db.flush()
        db.add(
            Assignment(
                event_id="service",
                person_id="draft-member",
                role="usher",
                solution_id=solution.id,
            )
        )
        db.commit()
        solution_id = solution.id

    with factory() as db:
        assignment, changed = claim_open_shift(
            db,
            org_id="claim-draft-history",
            event_id="service",
            person_id="live-member",
            role="usher",
            actor_email="live-member@example.test",
        )
        db.commit()
        assert changed is True
        assert assignment.solution_id is None

    with factory() as db:
        rows = db.query(Assignment).filter(Assignment.event_id == "service").all()
        assert len(rows) == 2
        assert any(row.solution_id == solution_id for row in rows)


@pytest.mark.integration
def test_concurrent_publishes_leave_exactly_one_coherent_roster(claim_database):
    factory = claim_database
    _seed(
        factory,
        org_id="publish-race",
        people={
            "admin": ["admin"],
            "first": ["volunteer", "usher"],
            "second": ["volunteer", "usher"],
        },
        events={"service": (0, {"usher": 1})},
    )
    solution_ids = [
        _scoped_solution(
            factory,
            org_id="publish-race",
            person_id=person_id,
            event_id="service",
        )
        for person_id in ("first", "second")
    ]
    barrier = Barrier(2, timeout=10)

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(
            executor.map(
                lambda solution_id: _publish(
                    factory,
                    barrier,
                    org_id="publish-race",
                    solution_id=solution_id,
                ),
                solution_ids,
            )
        )

    assert results == ["published", "published"]
    with factory() as db:
        active = (
            db.query(Solution)
            .filter(Solution.org_id == "publish-race", Solution.is_published.is_(True))
            .all()
        )
        assert len(active) == 1
        assert active[0].id in solution_ids
        assert db.query(AuditLog).filter(AuditLog.organization_id == "publish-race").count() == 2
        assert db.query(Notification).filter(Notification.org_id == "publish-race").count() == 2


@pytest.mark.integration
def test_publish_racing_last_slot_claim_has_one_valid_winner(claim_database):
    factory = claim_database
    _seed(
        factory,
        org_id="publish-claim-race",
        people={
            "admin": ["admin"],
            "scheduled": ["volunteer", "usher"],
            "claimant": ["volunteer", "usher"],
        },
        events={"service": (0, {"usher": 1})},
    )
    solution_id = _scoped_solution(
        factory,
        org_id="publish-claim-race",
        person_id="scheduled",
        event_id="service",
    )
    barrier = Barrier(2, timeout=10)

    def publish_attempt():
        return _publish(
            factory,
            barrier,
            org_id="publish-claim-race",
            solution_id=solution_id,
        )

    def claim_attempt():
        return _claim(
            factory,
            barrier,
            "publish-claim-race",
            "service",
            "claimant",
            "usher",
        )[0]

    with ThreadPoolExecutor(max_workers=2) as executor:
        publish_result = executor.submit(publish_attempt)
        claim_result = executor.submit(claim_attempt)
        outcomes = {publish_result.result(), claim_result.result()}

    assert outcomes in ({"published", "role_full"}, {"rejected", "won"})
    with factory() as db:
        active_solution = (
            db.query(Solution)
            .filter(
                Solution.org_id == "publish-claim-race",
                Solution.is_published.is_(True),
            )
            .first()
        )
        manual = (
            db.query(Assignment)
            .join(Event, Assignment.event_id == Event.id)
            .filter(
                Event.org_id == "publish-claim-race",
                Assignment.solution_id.is_(None),
            )
            .first()
        )
        assert (active_solution is not None) != (manual is not None)
        assert (
            db.query(AuditLog).filter(AuditLog.organization_id == "publish-claim-race").count() == 1
        )


@pytest.mark.integration
def test_concurrent_publish_and_rollback_serialize_to_one_active_solution(claim_database):
    factory = claim_database
    _seed(
        factory,
        org_id="publish-rollback-race",
        people={
            "admin": ["admin"],
            "first": ["volunteer", "usher"],
            "second": ["volunteer", "usher"],
            "third": ["volunteer", "usher"],
        },
        events={"service": (0, {"usher": 1})},
    )
    old_id = _scoped_solution(
        factory,
        org_id="publish-rollback-race",
        person_id="first",
        event_id="service",
    )
    current_id = _scoped_solution(
        factory,
        org_id="publish-rollback-race",
        person_id="second",
        event_id="service",
    )
    candidate_id = _scoped_solution(
        factory,
        org_id="publish-rollback-race",
        person_id="third",
        event_id="service",
    )
    assert (
        _publish(
            factory,
            None,
            org_id="publish-rollback-race",
            solution_id=old_id,
        )
        == "published"
    )
    assert (
        _publish(
            factory,
            None,
            org_id="publish-rollback-race",
            solution_id=current_id,
        )
        == "published"
    )
    barrier = Barrier(2, timeout=10)

    with ThreadPoolExecutor(max_workers=2) as executor:
        publish_future = executor.submit(
            _publish,
            factory,
            barrier,
            org_id="publish-rollback-race",
            solution_id=candidate_id,
        )
        rollback_future = executor.submit(
            _publish,
            factory,
            barrier,
            org_id="publish-rollback-race",
            solution_id=old_id,
            action=AuditAction.SOLUTION_ROLLED_BACK,
            rollback=True,
        )
        assert publish_future.result() == "published"
        assert rollback_future.result() == "published"

    with factory() as db:
        active = (
            db.query(Solution)
            .filter(
                Solution.org_id == "publish-rollback-race",
                Solution.is_published.is_(True),
            )
            .all()
        )
        assert len(active) == 1
        assert active[0].id in {old_id, candidate_id}
        assert (
            db.query(AuditLog).filter(AuditLog.organization_id == "publish-rollback-race").count()
            == 4
        )
