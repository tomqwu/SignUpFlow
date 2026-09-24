"""Validated, serialized schedule publication transactions."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Any, cast

from sqlalchemy.orm import Session

from api.core.constraints.persisted import PersistedConstraintError, map_database_constraints
from api.models import (
    Assignment,
    AuditAction,
    AuditLog,
    Constraint,
    Event,
    Notification,
    Person,
    Solution,
)
from api.services.allocation_service import (
    AllocationConflictError,
    lock_organization_allocations,
    require_person_available,
)
from api.services.assignment_response import carry_forward_current_responses
from api.timeutils import utcnow
from api.utils.audit_logger import log_audit_event


class PublicationConflictError(ValueError):
    """A publication rejection that leaves the active roster unchanged."""

    def __init__(self, message: str, *, status_code: int = 409):
        self.status_code = status_code
        super().__init__(message)


@dataclass(frozen=True)
class SolutionScope:
    range_start: date
    range_end: date
    event_ids: list[str]
    fingerprint: str


def _normalized_role_counts(event: Event) -> dict[str, int]:
    extra_data = cast(dict[str, Any], event.extra_data or {})
    raw = extra_data.get("role_counts", {})
    if not isinstance(raw, dict):
        return {}
    return {
        str(role): count
        for role, count in raw.items()
        if isinstance(count, int) and not isinstance(count, bool) and count > 0
    }


def _require_valid_role_counts(event: Event) -> dict[str, int]:
    extra_data = cast(dict[str, Any], event.extra_data or {})
    raw = extra_data.get("role_counts", {})
    if not isinstance(raw, dict):
        raise PublicationConflictError(
            f"{event.id} has invalid role requirements; repair the event and regenerate."
        )
    invalid = [
        str(role)
        for role, count in raw.items()
        if not isinstance(role, str)
        or not role.strip()
        or not isinstance(count, int)
        or isinstance(count, bool)
        or count < 1
    ]
    if invalid:
        raise PublicationConflictError(
            f"{event.id} has invalid role requirements for: {', '.join(sorted(invalid))}."
        )
    return {role: count for role, count in raw.items()}


def capture_solution_scope(
    events: list[Event],
    *,
    range_start: date,
    range_end: date,
    constraints: list[Constraint] | None = None,
) -> SolutionScope:
    """Capture every event in the solve window, including unfilled events."""
    rows = []
    for event in sorted(events, key=lambda row: str(row.id)):
        rows.append(
            {
                "id": str(event.id),
                "type": str(event.type),
                "start": event.start_time.isoformat(),
                "end": event.end_time.isoformat(),
                "resource_id": event.resource_id,
                "role_counts": _normalized_role_counts(event),
                "team_ids": sorted(str(link.team_id) for link in event.event_teams),
            }
        )
    payload = {
        "range_start": range_start.isoformat(),
        "range_end": range_end.isoformat(),
        "events": rows,
        "constraints": [
            {
                "key": str(row.key),
                "type": str(row.type),
                "weight": row.weight,
                "predicate": str(row.predicate),
                "params": row.params,
            }
            for row in sorted(constraints or [], key=lambda row: (str(row.key), int(row.id or 0)))
        ],
    }
    fingerprint = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return SolutionScope(
        range_start=range_start,
        range_end=range_end,
        event_ids=[row["id"] for row in rows],
        fingerprint=fingerprint,
    )


def _require_scope(solution: Solution) -> tuple[date, date, list[str], str]:
    event_ids = solution.scope_event_ids
    if (
        solution.scope_start is None
        or solution.scope_end is None
        or not isinstance(event_ids, list)
        or not event_ids
        or not solution.scope_fingerprint
    ):
        raise PublicationConflictError(
            "This legacy solution has no trustworthy solve scope; regenerate it before publishing."
        )
    if solution.scope_start > solution.scope_end:
        raise PublicationConflictError("The saved solve scope is invalid; regenerate the solution.")
    return (
        cast(date, solution.scope_start),
        cast(date, solution.scope_end),
        [str(event_id) for event_id in event_ids],
        cast(str, solution.scope_fingerprint),
    )


def _current_scope_events(
    db: Session, *, org_id: str, range_start: date, range_end: date
) -> list[Event]:
    return cast(
        list[Event],
        db.query(Event)
        .filter(
            Event.org_id == org_id,
            Event.start_time >= datetime.combine(range_start, time.min),
            Event.start_time <= datetime.combine(range_end, time.max),
        )
        .order_by(Event.id)
        .all(),
    )


def _validate_scope(
    db: Session, solution: Solution
) -> tuple[list[Event], list[Constraint], set[str]]:
    range_start, range_end, saved_ids, saved_fingerprint = _require_scope(solution)
    current_events = _current_scope_events(
        db,
        org_id=cast(str, solution.org_id),
        range_start=range_start,
        range_end=range_end,
    )
    current_constraints = (
        db.query(Constraint)
        .filter(Constraint.org_id == solution.org_id)
        .order_by(Constraint.id)
        .all()
    )
    current = capture_solution_scope(
        current_events,
        range_start=range_start,
        range_end=range_end,
        constraints=current_constraints,
    )
    if current.event_ids != sorted(saved_ids) or current.fingerprint != saved_fingerprint:
        raise PublicationConflictError(
            "Events, requirements, or constraints changed inside this solve window; "
            "regenerate before publishing."
        )
    return current_events, current_constraints, set(saved_ids)


def _require_preserved_horizon(
    db: Session, *, solution: Solution, prior_solutions: list[Solution], target_ids: set[str]
) -> None:
    now = utcnow()
    for prior in prior_solutions:
        _, _, prior_ids, _ = _require_scope(prior)
        future_ids = {
            event_id
            for event_id, start_time in db.query(Event.id, Event.start_time)
            .filter(Event.org_id == solution.org_id, Event.id.in_(prior_ids))
            .all()
            if start_time >= now
        }
        missing = sorted(future_ids - target_ids)
        if missing:
            raise PublicationConflictError(
                "Publishing would remove future events from the active horizon: "
                + ", ".join(missing)
                + ". Generate a full-horizon replacement."
            )


def _solution_assignments(db: Session, solution: Solution) -> list[Assignment]:
    return cast(
        list[Assignment],
        db.query(Assignment)
        .filter(Assignment.solution_id == solution.id)
        .order_by(Assignment.id)
        .all(),
    )


def _constraint_applies(event: Event, params: dict[str, Any]) -> bool:
    applies_to = params.get("applies_to", ["*"])
    return "*" in applies_to or event.type in applies_to


def _validate_hard_constraints(
    *,
    constraints: list[Constraint],
    roster: list[Assignment],
    events: dict[str, Event],
    people: dict[str, Person],
) -> None:
    try:
        map_database_constraints(constraints)
    except PersistedConstraintError as exc:
        raise PublicationConflictError(
            f"Saved constraint is invalid; repair it and regenerate: {exc}"
        ) from exc

    person_events: dict[str, list[Event]] = defaultdict(list)
    for assignment in roster:
        person_events[str(assignment.person_id)].append(events[str(assignment.event_id)])

    for constraint in constraints:
        if constraint.type != "hard":
            continue
        params = cast(dict[str, Any], constraint.params or {})
        if constraint.predicate == "max_assignments":
            period = cast(str, params["period"])
            maximum = cast(int, params["max_count"])
            for person_id, assigned_events in person_events.items():
                for anchor in assigned_events:
                    if not _constraint_applies(anchor, params):
                        continue
                    anchor_date = cast(datetime, anchor.start_time).date()
                    if period == "P1M":
                        window_start = anchor_date.replace(day=1)
                        window_end = (window_start + timedelta(days=32)).replace(day=1)
                    else:
                        window_days = int(period[1:-1])
                        half = window_days // 2
                        window_start = anchor_date - timedelta(days=half)
                        window_end = anchor_date + timedelta(days=window_days - half)
                    count = sum(
                        window_start <= cast(datetime, event.start_time).date() < window_end
                        for event in assigned_events
                    )
                    if count > maximum:
                        raise PublicationConflictError(
                            f"{people[person_id].name} exceeds saved constraint "
                            f"{constraint.key}: {count} assignments in {period}, maximum {maximum}."
                        )
        elif constraint.predicate == "min_gap_hours":
            minimum = cast(int, params["min_hours"])
            for person_id, assigned_events in person_events.items():
                ordered = sorted(
                    assigned_events, key=lambda event: cast(datetime, event.start_time)
                )
                for previous, current in zip(ordered, ordered[1:]):
                    if not _constraint_applies(current, params):
                        continue
                    gap = (
                        cast(datetime, current.start_time) - cast(datetime, previous.end_time)
                    ).total_seconds() / 3600
                    if gap < minimum:
                        raise PublicationConflictError(
                            f"{people[person_id].name} violates saved constraint "
                            f"{constraint.key}: {gap:g}h gap, minimum {minimum}h."
                        )


def _validate_roster(
    db: Session,
    *,
    solution: Solution,
    events: list[Event],
    constraints: list[Constraint],
    scope_ids: set[str],
) -> list[Assignment]:
    candidate = _solution_assignments(db, solution)
    manual = (
        db.query(Assignment)
        .join(Event, Assignment.event_id == Event.id)
        .join(Person, Assignment.person_id == Person.id)
        .filter(
            Assignment.solution_id.is_(None),
            Assignment.status != "declined",
            Event.org_id == solution.org_id,
            Person.org_id == solution.org_id,
            Event.id.in_(scope_ids),
        )
        .all()
    )
    roster = candidate + manual
    event_map = {str(event.id): event for event in events}
    role_counts = {str(event.id): _require_valid_role_counts(event) for event in events}
    person_ids = {str(row.person_id) for row in roster}
    people = {
        str(person.id): person
        for person in db.query(Person)
        .filter(Person.org_id == solution.org_id, Person.id.in_(person_ids))
        .all()
    }

    seen_event_person: set[tuple[str, str]] = set()
    person_windows: dict[str, list[tuple[datetime, datetime, str]]] = defaultdict(list)
    coverage: Counter[tuple[str, str]] = Counter()
    for row in roster:
        event = event_map.get(str(row.event_id))
        person = people.get(str(row.person_id))
        if event is None or person is None:
            raise PublicationConflictError(
                "The solution contains an event or member outside its organization."
            )
        if person.status != "active":
            raise PublicationConflictError(f"{person.name} is no longer an active member.")
        if row.status == "declined":
            raise PublicationConflictError(
                f"{person.name} declined {event.id}; repair the roster before publishing."
            )
        role = cast(str | None, row.role)
        required_roles = role_counts[str(event.id)]
        if required_roles and role not in required_roles:
            raise PublicationConflictError(
                f"{event.id} does not require assignment role {role or '(none)'}."
            )
        if role and role not in (person.roles or []):
            raise PublicationConflictError(
                f"{person.name} is no longer qualified for {role} on {event.id}."
            )
        try:
            require_person_available(db, person=person, event=event)
        except AllocationConflictError as exc:
            raise PublicationConflictError(f"{person.name} is unavailable for {event.id}.") from exc
        event_person = (str(event.id), str(person.id))
        if event_person in seen_event_person:
            raise PublicationConflictError(
                f"{person.name} has duplicate assignments on {event.id}."
            )
        seen_event_person.add(event_person)
        person_windows[str(person.id)].append(
            (
                cast(datetime, event.start_time),
                cast(datetime, event.end_time),
                str(event.id),
            )
        )
        if role:
            coverage[(str(event.id), role)] += 1

    for person_id, windows in person_windows.items():
        ordered = sorted(windows)
        for previous, current in zip(ordered, ordered[1:]):
            if previous[1] > current[0]:
                raise PublicationConflictError(
                    f"Member {person_id} overlaps on {previous[2]} and {current[2]}."
                )

    # A manual assignment made against an earlier schedule still counts here,
    # so a fresh solve that re-places the same slot reads as over-staffed. Name
    # the manual holder in that case: without it the refusal tells the
    # coordinator a slot is over capacity but not that their own override is
    # the cause, which leaves no way forward but guesswork.
    manual_holders: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in manual:
        role = cast(str | None, row.role)
        person = people.get(str(row.person_id))
        if role and person is not None:
            manual_holders[(str(row.event_id), role)].append(cast(str, person.name))

    gaps: list[str] = []
    excess: list[str] = []
    for event in events:
        for role, required in role_counts[str(event.id)].items():
            actual = coverage[(str(event.id), role)]
            if actual < required:
                gaps.append(f"{event.id}:{role} needs {required - actual} ({event.type})")
            elif actual > required:
                detail = f"{event.id}:{role} has {actual - required} extra ({event.type})"
                held_by = manual_holders.get((str(event.id), role))
                if held_by:
                    detail += (
                        f" including a manual assignment for {', '.join(sorted(held_by))};"
                        " remove it or regenerate the schedule"
                    )
                excess.append(detail)
    if gaps:
        raise PublicationConflictError("Required role shortages: " + "; ".join(gaps))
    if excess:
        raise PublicationConflictError("Role capacity exceeded: " + "; ".join(excess))
    _validate_hard_constraints(
        constraints=constraints,
        roster=roster,
        events=event_map,
        people=people,
    )
    if solution.hard_violations:
        raise PublicationConflictError(
            f"Solution records {solution.hard_violations} hard constraint violation(s)."
        )
    return candidate


def _queue_assignment_intent(
    db: Session, *, solution: Solution, assignments: list[Assignment]
) -> int:
    created = 0
    for assignment in assignments:
        if assignment.response_current and assignment.response_status == "accepted":
            continue
        delivery_key = (
            f"solution:{solution.id}:assignment:{assignment.id}:"
            f"r{assignment.commitment_revision}"
        )
        existing = (
            db.query(Notification)
            .filter(
                Notification.org_id == solution.org_id,
                Notification.delivery_key == delivery_key,
            )
            .first()
        )
        if existing is not None:
            continue
        db.add(
            Notification(
                org_id=solution.org_id,
                recipient_id=assignment.person_id,
                type="assignment",
                status="pending",
                event_id=assignment.event_id,
                delivery_key=delivery_key,
                template_data={
                    "event_id": assignment.event_id,
                    "solution_id": solution.id,
                    "commitment_revision": assignment.commitment_revision,
                },
            )
        )
        created += 1
    return created


def publish_solution_transaction(
    db: Session,
    *,
    solution_id: int,
    org_id: str,
    actor: Person,
    action: str = AuditAction.SOLUTION_PUBLISHED,
    require_previously_published: bool = False,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Solution:
    """Validate and activate one solution without committing the caller's transaction."""
    lock_organization_allocations(db, org_id)
    solution = (
        db.query(Solution).filter(Solution.id == solution_id, Solution.org_id == org_id).first()
    )
    if solution is None:
        raise PublicationConflictError("Solution not found.")
    if solution.is_published:
        return solution

    was_ever_published = (
        db.query(AuditLog)
        .filter(
            AuditLog.organization_id == org_id,
            AuditLog.resource_id == str(solution.id),
            AuditLog.action.in_([AuditAction.SOLUTION_PUBLISHED, AuditAction.SOLUTION_ROLLED_BACK]),
        )
        .count()
        > 0
    )
    if require_previously_published and not was_ever_published:
        raise PublicationConflictError(
            "Cannot roll back to a solution that has never been published.",
            status_code=400,
        )

    prior = (
        db.query(Solution)
        .filter(
            Solution.org_id == org_id,
            Solution.is_published.is_(True),
            Solution.id != solution.id,
        )
        .all()
    )
    events, constraints, scope_ids = _validate_scope(db, solution)
    _require_preserved_horizon(db, solution=solution, prior_solutions=prior, target_ids=scope_ids)
    carry_forward_current_responses(
        db,
        solution=solution,
        prior_solutions=prior,
        reset_stale_target_responses=was_ever_published,
    )
    assignments = _validate_roster(
        db,
        solution=solution,
        events=events,
        constraints=constraints,
        scope_ids=scope_ids,
    )

    for row in prior:
        cast(Any, row).is_published = False
        cast(Any, row).published_at = None
    cast(Any, solution).is_published = True
    cast(Any, solution).published_at = utcnow()
    notification_count = _queue_assignment_intent(db, solution=solution, assignments=assignments)
    log_audit_event(
        db,
        action=action,
        user_id=cast(str, actor.id),
        user_email=cast(str, actor.email),
        organization_id=org_id,
        resource_type="solution",
        resource_id=str(solution.id),
        details={
            "unpublished_prior_ids": [row.id for row in prior],
            "scope_event_ids": sorted(scope_ids),
            "notification_intent_count": notification_count,
        },
        ip_address=ip_address,
        user_agent=user_agent,
        commit=False,
    )
    db.flush()
    return solution


def unpublish_solution_transaction(
    db: Session,
    *,
    solution_id: int,
    org_id: str,
    actor: Person,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> Solution:
    """Unpublish and audit one solution without an intermediate commit."""
    lock_organization_allocations(db, org_id)
    solution = (
        db.query(Solution).filter(Solution.id == solution_id, Solution.org_id == org_id).first()
    )
    if solution is None:
        raise PublicationConflictError("Solution not found.")
    cast(Any, solution).is_published = False
    cast(Any, solution).published_at = None
    log_audit_event(
        db,
        action=AuditAction.SOLUTION_UNPUBLISHED,
        user_id=cast(str, actor.id),
        user_email=cast(str, actor.email),
        organization_id=org_id,
        resource_type="solution",
        resource_id=str(solution.id),
        ip_address=ip_address,
        user_agent=user_agent,
        commit=False,
    )
    db.flush()
    return solution
