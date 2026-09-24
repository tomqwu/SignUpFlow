"""Running the roster on the day itself: hours-away, in-progress, and finished shifts.

Every seeded fixture in this suite pushes events safely into the future --
`tests/e2e/_helpers.py::next_sunday_iso` lands at least seven days out and
`tests/playbooks/runtime.py::Playbook.__init__` starts fourteen days out -- so
the one case a coordinator actually panics about was unexercised: a volunteer
drops out of a shift that starts in three hours, or has already started, and
somebody has to fill it now.

That window is where the code's `now` boundaries live, and they do not agree
with each other:

* `assign_person_to_event` / `unassign_person_from_event`
  (`api/services/allocation_service.py`) never call `_require_future_event`, so
  a coordinator can staff an event that started an hour ago, or one that ended
  an hour ago.
* `release_person_work` and `replace_person_roles`
  (`api/services/qualification_service.py`) filter `Event.start_time >=
  utcnow()`, so the *instant an event starts* it stops being reopened by a
  deactivation or a qualification removal. The boundary is the start time, not
  the calendar day.
* `POST /api/v1/solver/solve` widens `from_date` with
  `datetime.combine(from_date, datetime.min.time())`, so a window starting
  today reaches back to midnight and sweeps in events that already happened
  today.
* `POST /api/v1/conflicts/check` reports a same-day double-booking as
  `can_assign=True` (advisory), while the allocation boundary that actually
  performs the assignment rejects it with 409.

These tests pin what the code does today, not what it arguably should do.

The clock is pinned to noon UTC on the current date via the supported
`SIGNUPFLOW_TEST_NOW` test clock. Without it, "three hours from now" crosses
midnight for anything run after 21:00 UTC and the same-day premise quietly
stops holding.
"""

from datetime import timedelta

import pytest

from api.models import Assignment, Event, Person
from api.timeutils import utcnow
from tests.api.conftest import (
    accept_invitation,
    add_timeoff,
    auth_headers,
    seed_invitation,
    seed_org,
    seed_user,
)

ORG = "same-day-org"
ADMIN_EMAIL = "admin@same-day.org"
ADMIN_PW = "AdminPass123!"
VOL_EMAIL = "sarah@same-day.org"
VOL_PW = "VolPass123!"
BACKUP_EMAIL = "ravi@same-day.org"
BACKUP_PW = "BackupPass123!"


# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _noon_today(monkeypatch):
    """Pin `utcnow()` to noon UTC on the real current date.

    Every offset in this module is expressed in hours around that instant, so
    the whole scenario stays inside one UTC day no matter when the suite runs.
    """
    pinned = utcnow().replace(hour=12, minute=0, second=0, microsecond=0)
    monkeypatch.setenv("SIGNUPFLOW_ALLOW_TEST_CLOCK", "true")
    monkeypatch.setenv("SIGNUPFLOW_TEST_NOW", pinned.isoformat() + "+00:00")
    return pinned


def _admin(client, org_id=ORG, email=ADMIN_EMAIL, password=ADMIN_PW):
    """Bootstrap an organization and its first admin, returning auth headers."""
    seed_org(client, org_id)
    seed_user(client, org_id, email, "Admin", password)
    return auth_headers(client, email, password)


def _volunteer(client, headers, org_id=ORG, email=VOL_EMAIL, name="Sarah", password=VOL_PW):
    """Add a volunteer the supported way: admin invitation, then acceptance."""
    invitation = seed_invitation(client, headers, org_id, email, name, roles=["usher"])
    return accept_invitation(client, invitation["token"], password=password)


def _create_event(
    client,
    headers,
    event_id,
    *,
    starts_in_hours,
    duration_hours=2,
    org_id=ORG,
    event_type="Evening Shift",
    role_counts=None,
):
    """Create an event at an hour offset from the pinned clock. Returns the response.

    `seed_event` from the conftest only takes whole days, which cannot express
    "three hours from now" or "started an hour ago" -- the entire subject here.
    """
    start = utcnow() + timedelta(hours=starts_in_hours)
    end = start + timedelta(hours=duration_hours)
    return client.post(
        "/api/v1/events/",
        json={
            "id": event_id,
            "org_id": org_id,
            "type": event_type,
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "extra_data": {"role_counts": role_counts or {}},
        },
        headers=headers,
    )


def _assign(client, headers, event_id, person_id, role="usher"):
    return client.post(
        f"/api/v1/events/{event_id}/assignments",
        json={"person_id": person_id, "action": "assign", "role": role},
        headers=headers,
    )


def _unassign(client, headers, event_id, person_id):
    return client.post(
        f"/api/v1/events/{event_id}/assignments",
        json={"person_id": person_id, "action": "unassign"},
        headers=headers,
    )


def _check_conflicts(client, headers, person_id, event_id):
    return client.post(
        "/api/v1/conflicts/check",
        json={"person_id": person_id, "event_id": event_id},
        headers=headers,
    )


def _assignments_in_org(db, org_id=ORG):
    """Assignment carries no org_id, so reach the tenant through its event."""
    return (
        db.query(Assignment)
        .join(Event, Event.id == Assignment.event_id)
        .filter(Event.org_id == org_id)
        .all()
    )


def _today_iso():
    return utcnow().date().isoformat()


# ---------------------------------------------------------------------------
# 1. Creating an event that happens today
# ---------------------------------------------------------------------------


@pytest.mark.no_mock_auth
class TestSameDayEventCreation:
    def test_admin_can_create_an_event_starting_in_three_hours(self, client, db):
        """An emergency shift added the same afternoon is accepted and listed."""
        headers = _admin(client)

        created = _create_event(
            client, headers, "same-day-soon", starts_in_hours=3, role_counts={"usher": 1}
        )
        assert created.status_code == 201, created.text
        assert created.json()["start_time"].startswith(_today_iso())

        listed = client.get(f"/api/v1/events/?org_id={ORG}", headers=headers)
        assert listed.status_code == 200, listed.text
        assert [row["id"] for row in listed.json()["items"]] == ["same-day-soon"]

    def test_imminent_event_is_upcoming_not_ongoing(self, client, db):
        """Three hours out, the computed status filters put it under 'upcoming'."""
        headers = _admin(client)
        _create_event(client, headers, "same-day-soon", starts_in_hours=3)

        upcoming = client.get(f"/api/v1/events/?org_id={ORG}&status=upcoming", headers=headers)
        ongoing = client.get(f"/api/v1/events/?org_id={ORG}&status=ongoing", headers=headers)

        assert [row["id"] for row in upcoming.json()["items"]] == ["same-day-soon"]
        assert ongoing.json()["items"] == []

    def test_the_api_happily_creates_an_event_that_already_started(self, client, db):
        """Event creation validates only `end > start`, never `start >= now`.

        `validate_time_range` (`api/utils/event_helpers.py`) is the only guard on
        the create path, so a start time in the past is accepted outright. That
        is what makes the in-progress and already-finished cases below reachable
        through the public API rather than only by seeding rows directly.
        """
        headers = _admin(client)

        in_progress = _create_event(client, headers, "same-day-running", starts_in_hours=-1)
        finished = _create_event(
            client, headers, "same-day-finished", starts_in_hours=-5, duration_hours=2
        )

        assert in_progress.status_code == 201, in_progress.text
        assert finished.status_code == 201, finished.text

        ongoing = client.get(f"/api/v1/events/?org_id={ORG}&status=ongoing", headers=headers)
        past = client.get(f"/api/v1/events/?org_id={ORG}&status=past", headers=headers)
        assert [row["id"] for row in ongoing.json()["items"]] == ["same-day-running"]
        assert [row["id"] for row in past.json()["items"]] == ["same-day-finished"]


# ---------------------------------------------------------------------------
# 2-3. Staffing and re-staffing a shift that is hours away
# ---------------------------------------------------------------------------


@pytest.mark.no_mock_auth
class TestSameDayStaffing:
    def test_admin_can_assign_to_an_event_starting_today(self, client, db):
        """The ordinary case: fill a slot for tonight."""
        headers = _admin(client)
        volunteer = _volunteer(client, headers)
        _create_event(
            client, headers, "same-day-shift", starts_in_hours=3, role_counts={"usher": 1}
        )

        assigned = _assign(client, headers, "same-day-shift", volunteer["person_id"])
        assert assigned.status_code == 200, assigned.text

        rows = _assignments_in_org(db)
        assert [(r.person_id, r.role) for r in rows] == [(volunteer["person_id"], "usher")]

    def test_dropout_is_refilled_by_a_different_qualified_person(self, client, db):
        """The headline scenario: Sarah bails at 3pm, Ravi covers the 3pm shift."""
        headers = _admin(client)
        sarah = _volunteer(client, headers)
        ravi = _volunteer(client, headers, email=BACKUP_EMAIL, name="Ravi", password=BACKUP_PW)
        _create_event(
            client, headers, "same-day-shift", starts_in_hours=3, role_counts={"usher": 1}
        )
        assert _assign(client, headers, "same-day-shift", sarah["person_id"]).status_code == 200

        dropped = _unassign(client, headers, "same-day-shift", sarah["person_id"])
        assert dropped.status_code == 200, dropped.text

        refilled = _assign(client, headers, "same-day-shift", ravi["person_id"])
        assert refilled.status_code == 200, refilled.text

        rows = _assignments_in_org(db)
        assert [(r.person_id, r.role) for r in rows] == [(ravi["person_id"], "usher")]

    def test_the_replacement_must_wait_for_the_dropout_to_be_released(self, client, db):
        """A single-seat role is full until the original assignment is deleted.

        There is no atomic "swap in a replacement" on this path: the coordinator
        has to unassign first, leaving the shift briefly unstaffed. Attempting
        the reverse order is refused with 409 `role_full`.
        """
        headers = _admin(client)
        sarah = _volunteer(client, headers)
        ravi = _volunteer(client, headers, email=BACKUP_EMAIL, name="Ravi", password=BACKUP_PW)
        _create_event(
            client, headers, "same-day-shift", starts_in_hours=3, role_counts={"usher": 1}
        )
        _assign(client, headers, "same-day-shift", sarah["person_id"])

        too_soon = _assign(client, headers, "same-day-shift", ravi["person_id"])
        assert too_soon.status_code == 409, too_soon.text
        assert "fully staffed" in too_soon.json()["detail"]

        _unassign(client, headers, "same-day-shift", sarah["person_id"])
        assert _assign(client, headers, "same-day-shift", ravi["person_id"]).status_code == 200

    def test_unassigning_someone_who_was_never_on_the_shift_is_a_404(self, client, db):
        """Double-clicking the drop-out button does not blow up mid-crisis."""
        headers = _admin(client)
        sarah = _volunteer(client, headers)
        _create_event(
            client, headers, "same-day-shift", starts_in_hours=3, role_counts={"usher": 1}
        )
        _assign(client, headers, "same-day-shift", sarah["person_id"])
        assert _unassign(client, headers, "same-day-shift", sarah["person_id"]).status_code == 200

        again = _unassign(client, headers, "same-day-shift", sarah["person_id"])
        assert again.status_code == 404, again.text


# ---------------------------------------------------------------------------
# 4. Conflict checking on the day
# ---------------------------------------------------------------------------


@pytest.mark.no_mock_auth
class TestSameDayConflictChecking:
    def test_time_off_covering_today_blocks_the_assignment(self, client, db):
        """A single-day time-off for today is reported and is genuinely enforced."""
        headers = _admin(client)
        sarah = _volunteer(client, headers)
        _create_event(
            client, headers, "same-day-shift", starts_in_hours=3, role_counts={"usher": 1}
        )
        add_timeoff(client, headers, sarah["person_id"], _today_iso(), _today_iso())

        checked = _check_conflicts(client, headers, sarah["person_id"], "same-day-shift")
        assert checked.status_code == 200, checked.text
        body = checked.json()
        assert body["has_conflicts"] is True
        assert [c["type"] for c in body["conflicts"]] == ["time_off"]
        assert body["can_assign"] is False

        refused = _assign(client, headers, "same-day-shift", sarah["person_id"])
        assert refused.status_code == 409, refused.text
        assert _assignments_in_org(db) == []

    def test_a_clean_same_day_slot_reports_no_conflicts(self, client, db):
        """The control case, so the assertions above mean something."""
        headers = _admin(client)
        sarah = _volunteer(client, headers)
        _create_event(
            client, headers, "same-day-shift", starts_in_hours=3, role_counts={"usher": 1}
        )

        body = _check_conflicts(client, headers, sarah["person_id"], "same-day-shift").json()
        assert body == {"has_conflicts": False, "conflicts": [], "can_assign": True}

    def test_double_booking_today_is_advisory_but_the_write_path_refuses_it(self, client, db):
        """`can_assign=True` for a same-day overlap, yet the assignment 409s.

        `POST /api/v1/conflicts/check` treats `double_booked` as a warning the
        coordinator may override -- only `already_assigned` and `time_off` are
        listed as blocking. `assign_person_to_event` disagrees:
        `_require_no_overlap` raises `overlap`, which the router maps to 409.
        So a UI that trusts `can_assign` will offer an override that the API
        then rejects. Pinned as-is; see the module docstring.
        """
        headers = _admin(client)
        sarah = _volunteer(client, headers)
        _create_event(
            client, headers, "same-day-first", starts_in_hours=3, role_counts={"usher": 1}
        )
        _create_event(
            client,
            headers,
            "same-day-overlap",
            starts_in_hours=4,
            role_counts={"usher": 1},
            event_type="Overlapping Shift",
        )
        assert _assign(client, headers, "same-day-first", sarah["person_id"]).status_code == 200

        body = _check_conflicts(client, headers, sarah["person_id"], "same-day-overlap").json()
        assert body["has_conflicts"] is True
        assert [c["type"] for c in body["conflicts"]] == ["double_booked"]
        assert body["conflicts"][0]["conflicting_event_id"] == "same-day-first"
        assert body["can_assign"] is True, "an overlap is only advisory to the checker"

        refused = _assign(client, headers, "same-day-overlap", sarah["person_id"])
        assert refused.status_code == 409, refused.text
        assert "overlapping assignment" in refused.json()["detail"]

    def test_back_to_back_shifts_today_are_not_a_conflict(self, client, db):
        """Overlap is strict: a shift starting exactly when another ends is fine."""
        headers = _admin(client)
        sarah = _volunteer(client, headers)
        _create_event(
            client,
            headers,
            "same-day-early",
            starts_in_hours=1,
            duration_hours=2,
            role_counts={"usher": 1},
        )
        _create_event(
            client,
            headers,
            "same-day-late",
            starts_in_hours=3,
            duration_hours=2,
            role_counts={"usher": 1},
            event_type="Late Shift",
        )
        _assign(client, headers, "same-day-early", sarah["person_id"])

        body = _check_conflicts(client, headers, sarah["person_id"], "same-day-late").json()
        assert body["has_conflicts"] is False
        assert _assign(client, headers, "same-day-late", sarah["person_id"]).status_code == 200

    def test_already_assigned_to_the_same_day_event_blocks_a_repeat(self, client, db):
        """Re-assigning the person already holding the shift is a blocking conflict."""
        headers = _admin(client)
        sarah = _volunteer(client, headers)
        _create_event(
            client, headers, "same-day-shift", starts_in_hours=3, role_counts={"usher": 1}
        )
        _assign(client, headers, "same-day-shift", sarah["person_id"])

        body = _check_conflicts(client, headers, sarah["person_id"], "same-day-shift").json()
        assert [c["type"] for c in body["conflicts"]] == ["already_assigned"]
        assert body["can_assign"] is False

        repeat = _assign(client, headers, "same-day-shift", sarah["person_id"])
        assert repeat.status_code == 409, repeat.text


# ---------------------------------------------------------------------------
# 5. A solver window that starts today
# ---------------------------------------------------------------------------


@pytest.mark.no_mock_auth
class TestSolverWindowStartingToday:
    def _solve(self, client, headers, from_date, to_date):
        return client.post(
            "/api/v1/solver/solve",
            json={"org_id": ORG, "from_date": from_date, "to_date": to_date, "mode": "strict"},
            headers=headers,
        )

    def test_a_window_starting_today_reaches_an_event_later_today(self, client, db):
        """`from_date=today` includes this afternoon's event.

        The router widens the bound with
        `datetime.combine(from_date, datetime.min.time())`, so the window opens
        at midnight rather than at the request time. A same-day re-solve
        therefore does see the shift that still needs covering.
        """
        headers = _admin(client)
        volunteer = _volunteer(client, headers)
        _create_event(
            client, headers, "same-day-shift", starts_in_hours=3, role_counts={"usher": 1}
        )

        solved = self._solve(client, headers, _today_iso(), _today_iso())
        assert solved.status_code == 200, solved.text
        assert solved.json()["assignment_count"] == 1

        rows = _assignments_in_org(db)
        assert [(r.event_id, r.person_id) for r in rows] == [
            ("same-day-shift", volunteer["person_id"])
        ]

    def test_the_window_also_sweeps_in_events_that_already_happened_today(self, client, db):
        """Midnight-anchored `from_date` reaches backwards into the finished part of today.

        An event that started five hours ago and ended three hours ago is still
        inside a `from_date=today` window, so the solver staffs it as if it were
        open work. Nothing on the solve path consults `utcnow()`.
        """
        headers = _admin(client)
        volunteer = _volunteer(client, headers)
        _create_event(
            client,
            headers,
            "same-day-finished",
            starts_in_hours=-5,
            duration_hours=2,
            role_counts={"usher": 1},
        )

        solved = self._solve(client, headers, _today_iso(), _today_iso())
        assert solved.status_code == 200, solved.text
        assert solved.json()["assignment_count"] == 1

        rows = _assignments_in_org(db)
        assert [r.event_id for r in rows] == ["same-day-finished"]
        assert rows[0].person_id == volunteer["person_id"]

    def test_a_window_starting_tomorrow_excludes_todays_shift(self, client, db):
        """The complement: today's event drops out and the solve has nothing to do."""
        headers = _admin(client)
        _volunteer(client, headers)
        _create_event(
            client, headers, "same-day-shift", starts_in_hours=3, role_counts={"usher": 1}
        )

        tomorrow = (utcnow().date() + timedelta(days=1)).isoformat()
        solved = self._solve(client, headers, tomorrow, tomorrow)

        assert solved.status_code == 400, solved.text
        assert "No events found" in solved.json()["detail"]


# ---------------------------------------------------------------------------
# 6. The `Event.start_time >= utcnow()` boundary
# ---------------------------------------------------------------------------


@pytest.mark.no_mock_auth
class TestInProgressAndFinishedEvents:
    """Where `start_time >= utcnow()` cuts, and where nothing cuts at all.

    An in-progress event sits exactly on the boundary that
    `release_person_work` and `replace_person_roles` use. The coordinator
    assign/unassign path has no such boundary, so the two halves of the system
    disagree about whether a running shift is still live work.
    """

    def _running_event_with_volunteer(
        self, client, event_id="same-day-running", starts_in_hours=-1
    ):
        headers = _admin(client)
        volunteer = _volunteer(client, headers)
        created = _create_event(
            client, headers, event_id, starts_in_hours=starts_in_hours, role_counts={"usher": 1}
        )
        assert created.status_code == 201, created.text
        return headers, volunteer

    # -- the write path ignores the boundary entirely -----------------------

    def test_a_coordinator_can_still_assign_to_an_event_in_progress(self, client, db):
        """A latecomer can be recorded on a shift that began an hour ago.

        `assign_person_to_event` never calls `_require_future_event` -- that
        guard only protects the volunteer-driven `claim_open_shift` and
        `cover_swap` flows (used by the web tier). The coordinator path is
        deliberately unbounded, which is what makes same-day recovery possible.
        """
        headers, volunteer = self._running_event_with_volunteer(client)

        assigned = _assign(client, headers, "same-day-running", volunteer["person_id"])
        assert assigned.status_code == 200, assigned.text
        assert len(_assignments_in_org(db)) == 1

    def test_a_coordinator_can_assign_to_an_event_that_already_ended(self, client, db):
        """Back-filling attendance after the fact is allowed with no warning.

        Same missing guard, one step further past the boundary: the event ended
        three hours ago and the assignment is still accepted as ordinary live
        work.
        """
        headers, volunteer = self._running_event_with_volunteer(
            client, event_id="same-day-finished", starts_in_hours=-5
        )

        assigned = _assign(client, headers, "same-day-finished", volunteer["person_id"])
        assert assigned.status_code == 200, assigned.text
        assert len(_assignments_in_org(db)) == 1

    def test_unassigning_from_an_in_progress_event_still_works(self, client, db):
        """A no-show can be struck off while the shift is running."""
        headers, volunteer = self._running_event_with_volunteer(client)
        _assign(client, headers, "same-day-running", volunteer["person_id"])

        dropped = _unassign(client, headers, "same-day-running", volunteer["person_id"])
        assert dropped.status_code == 200, dropped.text
        assert _assignments_in_org(db) == []

    def test_an_in_progress_assignment_stays_visible_to_the_member(self, client, db):
        """`/assignments/me` has no future-only filter, so the running shift shows.

        `member_visible_assignment` gates on publication only; it says nothing
        about time. The volunteer keeps seeing the shift they are currently
        working.
        """
        headers, volunteer = self._running_event_with_volunteer(client)
        _assign(client, headers, "same-day-running", volunteer["person_id"])

        mine = client.get("/api/v1/assignments/me", headers=auth_headers(client, VOL_EMAIL, VOL_PW))
        assert mine.status_code == 200, mine.text
        assert [row["event_id"] for row in mine.json()["items"]] == ["same-day-running"]

    # -- deactivation: the boundary is the start time, not the day ----------

    def test_deactivation_releases_a_shift_that_has_not_started_yet(self, client, db):
        """Today's later shift is still future work, so it is reopened."""
        headers, volunteer = self._running_event_with_volunteer(
            client, event_id="same-day-later", starts_in_hours=3
        )
        _assign(client, headers, "same-day-later", volunteer["person_id"])

        resp = client.post(f"/api/v1/people/{volunteer['person_id']}/deactivate", headers=headers)
        assert resp.status_code == 200, resp.text

        db.expire_all()
        assert _assignments_in_org(db) == []

    def test_deactivation_does_not_release_a_shift_already_under_way(self, client, db):
        """One hour after the start, `release_person_work` no longer touches it.

        `Event.start_time >= utcnow()` is false the moment the event begins, so
        deactivating the volunteer leaves the assignment standing. Two shifts
        on the same calendar day are treated differently purely by clock time:
        the running one survives, the later one (above) is released. The
        practical effect is that an emergency deactivation mid-shift does NOT
        surface the slot as needing cover.
        """
        headers, volunteer = self._running_event_with_volunteer(client)
        _assign(client, headers, "same-day-running", volunteer["person_id"])

        resp = client.post(f"/api/v1/people/{volunteer['person_id']}/deactivate", headers=headers)
        assert resp.status_code == 200, resp.text

        db.expire_all()
        person = (
            db.query(Person).filter(Person.org_id == ORG, Person.id == volunteer["person_id"]).one()
        )
        assert person.status == "inactive"
        surviving = _assignments_in_org(db)
        assert len(surviving) == 1, "the in-progress shift was released after all"
        assert surviving[0].person_id == volunteer["person_id"]

    def test_deactivation_splits_a_single_day_at_the_current_moment(self, client, db):
        """Both shifts are today; only the not-yet-started one is reopened."""
        headers = _admin(client)
        volunteer = _volunteer(client, headers)
        _create_event(
            client, headers, "same-day-running", starts_in_hours=-1, role_counts={"usher": 1}
        )
        _create_event(
            client,
            headers,
            "same-day-later",
            starts_in_hours=3,
            role_counts={"usher": 1},
            event_type="Later Shift",
        )
        _assign(client, headers, "same-day-running", volunteer["person_id"])
        _assign(client, headers, "same-day-later", volunteer["person_id"])
        assert len(_assignments_in_org(db)) == 2

        client.post(f"/api/v1/people/{volunteer['person_id']}/deactivate", headers=headers)

        db.expire_all()
        assert [r.event_id for r in _assignments_in_org(db)] == ["same-day-running"]

    # -- qualification removal uses the same boundary -----------------------

    def test_removing_a_qualification_does_not_reopen_an_in_progress_shift(self, client, db):
        """`replace_person_roles` shares the boundary, with the same consequence.

        Stripping the `usher` qualification mid-shift leaves the person rostered
        as an usher on the event currently running, while the later shift today
        is reopened.
        """
        headers = _admin(client)
        volunteer = _volunteer(client, headers)
        _create_event(
            client, headers, "same-day-running", starts_in_hours=-1, role_counts={"usher": 1}
        )
        _create_event(
            client,
            headers,
            "same-day-later",
            starts_in_hours=3,
            role_counts={"usher": 1},
            event_type="Later Shift",
        )
        _assign(client, headers, "same-day-running", volunteer["person_id"])
        _assign(client, headers, "same-day-later", volunteer["person_id"])

        updated = client.put(
            f"/api/v1/people/{volunteer['person_id']}",
            json={"roles": ["volunteer"]},
            headers=headers,
        )
        assert updated.status_code == 200, updated.text

        db.expire_all()
        remaining = _assignments_in_org(db)
        assert [(r.event_id, r.role) for r in remaining] == [("same-day-running", "usher")]
        person = (
            db.query(Person).filter(Person.org_id == ORG, Person.id == volunteer["person_id"]).one()
        )
        assert "usher" not in (person.roles or []), "still rostered for a role they no longer hold"

    def test_a_shift_starting_this_instant_counts_as_future_work(self, client, db):
        """The comparison is `>=`, so start == now falls on the future side.

        A zero-offset event is the exact boundary value. It is reopened by
        deactivation, unlike the one-hour-old event above.
        """
        headers = _admin(client)
        volunteer = _volunteer(client, headers)
        _create_event(client, headers, "same-day-now", starts_in_hours=0, role_counts={"usher": 1})
        _assign(client, headers, "same-day-now", volunteer["person_id"])

        client.post(f"/api/v1/people/{volunteer['person_id']}/deactivate", headers=headers)

        db.expire_all()
        assert _assignments_in_org(db) == []
