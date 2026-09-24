"""Recovering from a published schedule that turned out to be wrong.

A coordinator publishes, spots a mistake, and has to undo it. Both halves of
that undo are covered in isolation already — unpublish by
``tests/e2e/test_notif_assign_unpublish.py::test_publish_then_unpublish_state``
and friends, rollback by
``tests/api/test_solution_compare_rollback.py::test_admin_can_rollback_to_prior_published``
— but nothing walked the whole chain (publish, unpublish, correct, re-solve,
republish), and nothing at all pinned the half the volunteer experiences: what
their own schedule shows while the correction is in flight, and what they are
told about it.

These tests pin ACTUAL behavior, including three places where it is surprising:

1. Whether a volunteer's acceptance survives a correction depends entirely on
   whether the coordinator unpublished first. Republishing straight over the
   live solution carries the acceptance forward
   (``carry_forward_current_responses``); unpublishing first has no prior
   published solution to carry from, so the same end state arrives with the
   acceptance silently dropped.
2. Unpublishing tells nobody. Publication queues one ``Notification`` per
   assignment; withdrawing that schedule queues none, so a volunteer who was
   emailed about a shift is never told it no longer exists.
3. Correcting an event *after* unpublishing also tells nobody, because
   ``update_event`` only notifies assignees of visible (published or manual)
   work — yet it still bumps every assignment's ``commitment_revision``, so the
   acceptance is invalidated in silence.

Rollback is not a recovery route after a correction at all: it revalidates the
target's solve scope, which the correction has just invalidated.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from api.models import Assignment, Event, Notification, Solution
from tests.api.conftest import (
    accept_invitation,
    auth_headers,
    seed_event,
    seed_invitation,
    seed_org,
    seed_user,
)

ADMIN_PW = "AdminPass123!"
VOL_PW = "VolPass123!"

# One event three weeks out; the solve window brackets it generously so a
# one-hour correction never moves the event out of scope.
EVENT_DAYS_OUT = 21
WINDOW_START_DAYS = 14
WINDOW_END_DAYS = 45


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _admin(client, org_id: str) -> dict:
    """Bootstrap the organization with its first admin and return auth headers."""
    email = f"admin@{org_id}.example"
    seed_org(client, org_id)
    seed_user(client, org_id, email, "Admin", ADMIN_PW)
    return auth_headers(client, email, ADMIN_PW)


def _volunteer(client, headers: dict, org_id: str, name: str, qualifications: list[str]) -> str:
    """Invite one volunteer holding the given scheduling qualifications."""
    invitation = seed_invitation(
        client,
        headers,
        org_id,
        f"{name}@{org_id}.example",
        name.title(),
        roles=["volunteer", *qualifications],
    )
    return accept_invitation(client, invitation["token"], password=VOL_PW)["person_id"]


def _volunteer_headers(client, org_id: str, name: str) -> dict:
    return auth_headers(client, f"{name}@{org_id}.example", VOL_PW)


def _solve(client, headers: dict, org_id: str) -> int:
    """Run the real solver over the window containing the seeded events."""
    now = datetime.now()
    response = client.post(
        "/api/v1/solver/solve",
        json={
            "org_id": org_id,
            "from_date": (now + timedelta(days=WINDOW_START_DAYS)).date().isoformat(),
            "to_date": (now + timedelta(days=WINDOW_END_DAYS)).date().isoformat(),
            "mode": "strict",
            "change_min": False,
        },
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return response.json()["solution_id"]


def _publish(client, headers: dict, solution_id: int):
    return client.post(f"/api/v1/solutions/{solution_id}/publish", headers=headers)


def _unpublish(client, headers: dict, solution_id: int):
    return client.post(f"/api/v1/solutions/{solution_id}/unpublish", headers=headers)


def _rollback(client, headers: dict, solution_id: int):
    return client.post(f"/api/v1/solutions/{solution_id}/rollback", headers=headers)


def _published_solution_ids(db, org_id: str) -> list[int]:
    return [
        row.id
        for row in db.query(Solution)
        .filter(Solution.org_id == org_id, Solution.is_published.is_(True))
        .all()
    ]


def _solution_roster(db, org_id: str, solution_id: int) -> set[tuple[str, str, str]]:
    """(event_id, person_id, role) triples of one solution, reached org-scoped."""
    rows = (
        db.query(Assignment)
        .join(Event, Assignment.event_id == Event.id)
        .filter(Event.org_id == org_id, Assignment.solution_id == solution_id)
        .all()
    )
    return {(row.event_id, row.person_id, row.role) for row in rows}


def _solution_assignments(db, org_id: str, solution_id: int) -> list[Assignment]:
    return (
        db.query(Assignment)
        .join(Event, Assignment.event_id == Event.id)
        .filter(Event.org_id == org_id, Assignment.solution_id == solution_id)
        .order_by(Assignment.id)
        .all()
    )


def _notifications(db, org_id: str) -> list[Notification]:
    return (
        db.query(Notification).filter(Notification.org_id == org_id).order_by(Notification.id).all()
    )


def _my_assignments(client, vol_headers: dict) -> list[dict]:
    response = client.get("/api/v1/assignments/me", headers=vol_headers)
    assert response.status_code == 200, response.text
    return response.json()["items"]


def _event_row(db, org_id: str, event_id: str) -> Event:
    return db.query(Event).filter(Event.org_id == org_id, Event.id == event_id).one()


def _correct_event_time(client, headers: dict, event_id: str, *, hours: int = 1):
    """The correction a coordinator actually makes: the service is at the wrong hour."""
    now = datetime.now()
    start = now + timedelta(days=EVENT_DAYS_OUT, hours=hours)
    response = client.put(
        f"/api/v1/events/{event_id}",
        json={
            "start_time": start.isoformat(),
            "end_time": (start + timedelta(hours=2)).isoformat(),
        },
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return response.json()


def _one_event_one_usher(client, org_id: str, *, event_id: str, volunteers: int = 1):
    """Admin, `volunteers` qualified ushers, and a single event needing one usher."""
    headers = _admin(client, org_id)
    names = [f"vol{index}" for index in range(volunteers)]
    person_ids = [_volunteer(client, headers, org_id, name, ["usher"]) for name in names]
    seed_event(
        client,
        headers,
        org_id,
        event_id,
        days_from_now=EVENT_DAYS_OUT,
        role_counts={"usher": 1},
    )
    return headers, names, person_ids


# ---------------------------------------------------------------------------
# 1. The full recovery chain
# ---------------------------------------------------------------------------


@pytest.mark.no_mock_auth
class TestFullRecoveryChain:
    ORG = "recovery-chain"
    EVENT = "recovery-chain-service"

    def test_publish_unpublish_correct_resolve_republish(self, client, db):
        """The corrected solution ends up live and the mistaken one does not."""
        headers, _, _ = _one_event_one_usher(client, self.ORG, event_id=self.EVENT)
        wrong_start = _event_row(db, self.ORG, self.EVENT).start_time

        mistaken = _solve(client, headers, self.ORG)
        assert _publish(client, headers, mistaken).status_code == 200

        withdrawn = _unpublish(client, headers, mistaken)
        assert withdrawn.status_code == 200, withdrawn.text
        assert withdrawn.json()["is_published"] is False
        assert _published_solution_ids(db, self.ORG) == []

        _correct_event_time(client, headers, self.EVENT)

        corrected = _solve(client, headers, self.ORG)
        assert corrected != mistaken
        republished = _publish(client, headers, corrected)
        assert republished.status_code == 200, republished.text

        db.expire_all()
        assert _published_solution_ids(db, self.ORG) == [corrected]
        assert db.get(Solution, mistaken).is_published is False
        assert db.get(Solution, mistaken).published_at is None

        # The live roster points at the corrected event, and the whole org
        # holds exactly one assignment per solution — nothing was orphaned.
        live = client.get(f"/api/v1/solutions/{corrected}/assignments", headers=headers).json()
        assert live["total_assignments"] == 1
        assert live["events"][0]["event_id"] == self.EVENT
        corrected_start = _event_row(db, self.ORG, self.EVENT).start_time
        assert corrected_start != wrong_start, "the correction must have moved the event"
        assert live["events"][0]["event_start"].startswith(corrected_start.isoformat()[:16])
        assert not live["events"][0]["event_start"].startswith(wrong_start.isoformat()[:16])

    def test_the_mistaken_solution_cannot_be_published_again_after_the_correction(self, client, db):
        """The stale solve window is the guard that stops the mistake returning."""
        headers, _, _ = _one_event_one_usher(client, self.ORG, event_id=self.EVENT)
        mistaken = _solve(client, headers, self.ORG)
        assert _publish(client, headers, mistaken).status_code == 200
        assert _unpublish(client, headers, mistaken).status_code == 200

        _correct_event_time(client, headers, self.EVENT)

        refused = _publish(client, headers, mistaken)
        assert refused.status_code == 409, refused.text
        assert "regenerate" in refused.json()["detail"].lower()
        db.expire_all()
        assert _published_solution_ids(db, self.ORG) == []

    def test_correcting_before_unpublishing_reaches_the_same_place(self, client, db):
        """Order does not matter to the final roster; it does matter to the people (see below)."""
        headers, _, _ = _one_event_one_usher(client, self.ORG, event_id=self.EVENT)
        mistaken = _solve(client, headers, self.ORG)
        assert _publish(client, headers, mistaken).status_code == 200

        _correct_event_time(client, headers, self.EVENT)
        corrected = _solve(client, headers, self.ORG)

        # No unpublish at all: publishing the replacement retires the old one.
        assert _publish(client, headers, corrected).status_code == 200, "correction must publish"
        db.expire_all()
        assert _published_solution_ids(db, self.ORG) == [corrected]


# ---------------------------------------------------------------------------
# 2. What the volunteer sees while the schedule is withdrawn
# ---------------------------------------------------------------------------


@pytest.mark.no_mock_auth
class TestVolunteerViewDuringTheUnpublishedWindow:
    ORG = "recovery-window"
    EVENT = "recovery-window-service"

    def test_unpublishing_hides_the_shift_from_the_volunteers_own_schedule(self, client, db):
        """`/assignments/me` filters on publication, so the shift disappears."""
        headers, names, person_ids = _one_event_one_usher(client, self.ORG, event_id=self.EVENT)
        vol_headers = _volunteer_headers(client, self.ORG, names[0])

        solution = _solve(client, headers, self.ORG)
        assert _my_assignments(client, vol_headers) == [], "draft work must stay invisible"

        assert _publish(client, headers, solution).status_code == 200
        mine = _my_assignments(client, vol_headers)
        assert [row["person_id"] for row in mine] == [person_ids[0]]
        assert mine[0]["event_id"] == self.EVENT

        assert _unpublish(client, headers, solution).status_code == 200
        assert (
            _my_assignments(client, vol_headers) == []
        ), "the shift vanishes from the volunteer's schedule the moment it is withdrawn"

        # The row itself survives; only its visibility changed.
        assert len(_solution_roster(db, self.ORG, solution)) == 1

    def test_the_notification_they_already_received_outlives_the_schedule(self, client, db):
        """They keep the message about a shift their schedule no longer shows."""
        headers, names, person_ids = _one_event_one_usher(client, self.ORG, event_id=self.EVENT)
        vol_headers = _volunteer_headers(client, self.ORG, names[0])
        solution = _solve(client, headers, self.ORG)
        assert _publish(client, headers, solution).status_code == 200

        inbox = client.get(f"/api/v1/notifications/?org_id={self.ORG}", headers=vol_headers).json()
        assert inbox["total"] == 1
        assert inbox["notifications"][0]["type"] == "assignment"
        assert inbox["notifications"][0]["recipient_id"] == person_ids[0]

        assert _unpublish(client, headers, solution).status_code == 200

        after = client.get(f"/api/v1/notifications/?org_id={self.ORG}", headers=vol_headers).json()
        assert after["total"] == 1, "the assignment notice is not retracted or superseded"
        assert _my_assignments(client, vol_headers) == []
        # So the volunteer holds a notice about a shift that /assignments/me
        # no longer lists, with nothing in the inbox explaining the gap.

    def test_the_corrected_shift_comes_back_when_the_replacement_is_published(self, client, db):
        """After the republish the volunteer sees the corrected work again."""
        headers, names, person_ids = _one_event_one_usher(client, self.ORG, event_id=self.EVENT)
        vol_headers = _volunteer_headers(client, self.ORG, names[0])
        first = _solve(client, headers, self.ORG)
        assert _publish(client, headers, first).status_code == 200
        assert _unpublish(client, headers, first).status_code == 200
        _correct_event_time(client, headers, self.EVENT)

        second = _solve(client, headers, self.ORG)
        assert _publish(client, headers, second).status_code == 200

        mine = _my_assignments(client, vol_headers)
        assert [(row["event_id"], row["person_id"]) for row in mine] == [
            (self.EVENT, person_ids[0])
        ]
        assert len(mine) == 1, "the withdrawn solution's row must not resurface alongside it"
        db.expire_all()
        assert _published_solution_ids(db, self.ORG) == [second]


# ---------------------------------------------------------------------------
# 3. Who gets told
# ---------------------------------------------------------------------------


@pytest.mark.no_mock_auth
class TestWhoIsToldAboutTheWithdrawal:
    ORG = "recovery-notice"
    EVENT = "recovery-notice-service"

    def test_publishing_queues_one_notice_per_assignee(self, client, db):
        """The baseline the withdrawal is compared against."""
        headers, _, person_ids = _one_event_one_usher(client, self.ORG, event_id=self.EVENT)
        solution = _solve(client, headers, self.ORG)

        assert _notifications(db, self.ORG) == []
        assert _publish(client, headers, solution).status_code == 200

        db.expire_all()
        queued = _notifications(db, self.ORG)
        assert [row.type for row in queued] == ["assignment"]
        assert [row.recipient_id for row in queued] == [person_ids[0]]
        assert queued[0].delivery_key.startswith(f"solution:{solution}:assignment:")

    def test_unpublishing_notifies_nobody(self, client, db):
        """Withdrawing a live schedule queues no notification of any kind."""
        headers, _, _ = _one_event_one_usher(client, self.ORG, event_id=self.EVENT)
        solution = _solve(client, headers, self.ORG)
        assert _publish(client, headers, solution).status_code == 200
        db.expire_all()
        before = [row.id for row in _notifications(db, self.ORG)]
        assert len(before) == 1

        assert _unpublish(client, headers, solution).status_code == 200

        db.expire_all()
        after = _notifications(db, self.ORG)
        assert [
            row.id for row in after
        ] == before, "unpublish is silent: the assignees are never told the schedule was pulled"

    def test_correcting_the_event_after_unpublishing_is_also_silent(self, client, db):
        """`update_event` only notices published or manual work, so nobody hears."""
        headers, _, _ = _one_event_one_usher(client, self.ORG, event_id=self.EVENT)
        solution = _solve(client, headers, self.ORG)
        assert _publish(client, headers, solution).status_code == 200
        assert _unpublish(client, headers, solution).status_code == 200
        db.expire_all()
        before = [row.id for row in _notifications(db, self.ORG)]

        _correct_event_time(client, headers, self.EVENT)

        db.expire_all()
        assert [
            row.id for row in _notifications(db, self.ORG)
        ] == before, "moving the event while the schedule is withdrawn tells nobody"

    def test_correcting_the_event_while_still_published_does_notify(self, client, db):
        """The contrast: keep it published and the assignee gets an update notice."""
        headers, _, person_ids = _one_event_one_usher(client, self.ORG, event_id=self.EVENT)
        solution = _solve(client, headers, self.ORG)
        assert _publish(client, headers, solution).status_code == 200

        _correct_event_time(client, headers, self.EVENT)

        db.expire_all()
        updates = [row for row in _notifications(db, self.ORG) if row.type == "update"]
        assert [row.recipient_id for row in updates] == [person_ids[0]]
        assert updates[0].delivery_key.startswith(f"event:{self.EVENT}:update:")

    def test_republishing_the_correction_queues_a_fresh_notice(self, client, db):
        """The corrected schedule announces itself, under its own delivery key."""
        headers, _, person_ids = _one_event_one_usher(client, self.ORG, event_id=self.EVENT)
        first = _solve(client, headers, self.ORG)
        assert _publish(client, headers, first).status_code == 200
        assert _unpublish(client, headers, first).status_code == 200
        _correct_event_time(client, headers, self.EVENT)
        second = _solve(client, headers, self.ORG)

        assert _publish(client, headers, second).status_code == 200

        db.expire_all()
        assignment_notices = [
            row for row in _notifications(db, self.ORG) if row.type == "assignment"
        ]
        assert len(assignment_notices) == 2
        assert {row.recipient_id for row in assignment_notices} == {person_ids[0]}
        keys = [row.delivery_key for row in assignment_notices]
        assert keys[0].startswith(f"solution:{first}:assignment:")
        assert keys[1].startswith(f"solution:{second}:assignment:")


# ---------------------------------------------------------------------------
# 4. Rollback after a bad republish
# ---------------------------------------------------------------------------


@pytest.mark.no_mock_auth
class TestRollbackAfterABadRepublish:
    ORG = "recovery-rollback"
    EVENT = "recovery-rollback-service"

    def test_rollback_restores_the_earlier_schedule(self, client, db):
        """Publish A, publish B, then put A back: A is live and B is not."""
        headers, names, person_ids = _one_event_one_usher(client, self.ORG, event_id=self.EVENT)
        vol_headers = _volunteer_headers(client, self.ORG, names[0])
        first = _solve(client, headers, self.ORG)
        second = _solve(client, headers, self.ORG)
        assert _publish(client, headers, first).status_code == 200
        assert _publish(client, headers, second).status_code == 200
        db.expire_all()
        assert _published_solution_ids(db, self.ORG) == [second]

        restored = _rollback(client, headers, first)
        assert restored.status_code == 200, restored.text
        assert restored.json()["is_published"] is True

        db.expire_all()
        assert _published_solution_ids(db, self.ORG) == [first]
        assert db.get(Solution, second).is_published is False
        assert db.get(Solution, second).published_at is None

        # The volunteer sees exactly one shift, the one belonging to A.
        mine = _my_assignments(client, vol_headers)
        assert len(mine) == 1
        assert mine[0]["person_id"] == person_ids[0]
        assert mine[0]["id"] in {row.id for row in _solution_assignments(db, self.ORG, first)}

    def test_rollback_is_refused_once_the_schedule_itself_was_corrected(self, client, db):
        """Rollback revalidates the target's solve window, which a correction invalidates.

        So rollback recovers a bad *choice of roster*, never a bad *event*: once
        the event is fixed, the only way back is a fresh solve.
        """
        headers, _, _ = _one_event_one_usher(client, self.ORG, event_id=self.EVENT)
        first = _solve(client, headers, self.ORG)
        assert _publish(client, headers, first).status_code == 200

        _correct_event_time(client, headers, self.EVENT)
        second = _solve(client, headers, self.ORG)
        assert _publish(client, headers, second).status_code == 200

        refused = _rollback(client, headers, first)
        assert refused.status_code == 409, refused.text
        assert "regenerate" in refused.json()["detail"].lower()

        db.expire_all()
        assert _published_solution_ids(db, self.ORG) == [
            second
        ], "a refused rollback must leave the live schedule alone"

    def test_rollback_after_an_unpublish_republishes_without_a_live_predecessor(self, client, db):
        """Unpublish then roll back: the withdrawn schedule returns to life."""
        headers, names, _ = _one_event_one_usher(client, self.ORG, event_id=self.EVENT)
        vol_headers = _volunteer_headers(client, self.ORG, names[0])
        solution = _solve(client, headers, self.ORG)
        assert _publish(client, headers, solution).status_code == 200
        assert _unpublish(client, headers, solution).status_code == 200
        assert _my_assignments(client, vol_headers) == []

        restored = _rollback(client, headers, solution)

        assert restored.status_code == 200, restored.text
        db.expire_all()
        assert _published_solution_ids(db, self.ORG) == [solution]
        assert len(_my_assignments(client, vol_headers)) == 1


# ---------------------------------------------------------------------------
# 5. What happens to an acceptance
# ---------------------------------------------------------------------------


@pytest.mark.no_mock_auth
class TestAcceptanceAcrossTheRecovery:
    ORG = "recovery-accept"
    EVENT = "recovery-accept-service"

    def _accepted_publication(self, client, db):
        """Publish a solution and have the assignee accept their shift."""
        headers, names, person_ids = _one_event_one_usher(client, self.ORG, event_id=self.EVENT)
        vol_headers = _volunteer_headers(client, self.ORG, names[0])
        solution = _solve(client, headers, self.ORG)
        assert _publish(client, headers, solution).status_code == 200

        assignment = _solution_assignments(db, self.ORG, solution)[0]
        accepted = client.post(f"/api/v1/assignments/{assignment.id}/accept", headers=vol_headers)
        assert accepted.status_code == 200, accepted.text
        assert accepted.json()["response_status"] == "accepted"
        return headers, vol_headers, person_ids[0], solution

    def test_acceptance_carries_forward_when_the_replacement_publishes_directly(self, client, db):
        """With the old solution still live, the acceptance moves to the new one."""
        headers, _, person_id, first = self._accepted_publication(client, db)

        second = _solve(client, headers, self.ORG)
        assert _publish(client, headers, second).status_code == 200

        db.expire_all()
        carried = _solution_assignments(db, self.ORG, second)[0]
        assert carried.response_status == "accepted"
        assert carried.responded_by_person_id == person_id
        assert carried.response_current is True
        # An already-accepted commitment queues no new notice.
        assert len([row for row in _notifications(db, self.ORG) if row.type == "assignment"]) == 1

    def test_unpublishing_first_silently_drops_the_acceptance(self, client, db):
        """Same destination, opposite outcome — only the unpublish differs.

        `carry_forward_current_responses` reads the org's currently *published*
        solutions. Unpublishing leaves none, so there is nothing to carry from
        and the replacement starts at "pending" although nothing about the
        volunteer's shift changed.
        """
        headers, vol_headers, person_id, first = self._accepted_publication(client, db)

        assert _unpublish(client, headers, first).status_code == 200
        second = _solve(client, headers, self.ORG)
        assert _publish(client, headers, second).status_code == 200

        db.expire_all()
        replacement = _solution_assignments(db, self.ORG, second)[0]
        assert replacement.response_status == "pending"
        assert replacement.responded_by_person_id is None
        assert replacement.response_current is False

        # The original acceptance is still on the retired solution's row, so the
        # record says "accepted" while the live schedule says "pending".
        retired = _solution_assignments(db, self.ORG, first)[0]
        assert retired.response_status == "accepted"
        assert retired.responded_by_person_id == person_id

        # The volunteer's own view shows the shift as unanswered again.
        mine = _my_assignments(client, vol_headers)
        assert len(mine) == 1
        assert mine[0]["response_status"] == "pending"

    def test_correcting_the_event_invalidates_the_acceptance_without_telling_anyone(
        self, client, db
    ):
        """The revision bump reaches withdrawn work; the notification does not."""
        headers, vol_headers, _, first = self._accepted_publication(client, db)
        assert _unpublish(client, headers, first).status_code == 200
        db.expire_all()
        before_revision = _solution_assignments(db, self.ORG, first)[0].commitment_revision
        before_notices = [row.id for row in _notifications(db, self.ORG)]

        _correct_event_time(client, headers, self.EVENT)

        db.expire_all()
        reset = _solution_assignments(db, self.ORG, first)[0]
        assert reset.commitment_revision == before_revision + 1
        assert reset.response_status == "pending", "the acceptance was wiped"
        assert reset.responded_at is None
        assert [
            row.id for row in _notifications(db, self.ORG)
        ] == before_notices, (
            "the acceptance was invalidated with no notice to the person who gave it"
        )
        assert _my_assignments(client, vol_headers) == []

    def test_the_corrected_republish_asks_the_volunteer_again(self, client, db):
        """End to end: after the whole chain the shift is live, pending, and re-announced."""
        headers, vol_headers, person_id, first = self._accepted_publication(client, db)
        assert _unpublish(client, headers, first).status_code == 200
        _correct_event_time(client, headers, self.EVENT)
        second = _solve(client, headers, self.ORG)
        assert _publish(client, headers, second).status_code == 200

        db.expire_all()
        mine = _my_assignments(client, vol_headers)
        assert len(mine) == 1
        assert mine[0]["response_status"] == "pending"
        assert mine[0]["person_id"] == person_id

        notices = [row for row in _notifications(db, self.ORG) if row.type == "assignment"]
        assert len(notices) == 2, "the corrected schedule queues its own assignment notice"
        assert notices[-1].delivery_key.startswith(f"solution:{second}:assignment:")

        # Re-accepting the corrected commitment works and is recorded fresh.
        reaccepted = client.post(f"/api/v1/assignments/{mine[0]['id']}/accept", headers=vol_headers)
        assert reaccepted.status_code == 200, reaccepted.text
        assert reaccepted.json()["response_status"] == "accepted"

    def test_a_declined_shift_blocks_the_corrected_republish(self, client, db):
        """A decline is not cleared by the recovery, so publication refuses the roster."""
        headers, names, _ = _one_event_one_usher(client, self.ORG, event_id=self.EVENT)
        vol_headers = _volunteer_headers(client, self.ORG, names[0])
        first = _solve(client, headers, self.ORG)
        assert _publish(client, headers, first).status_code == 200
        assignment = _solution_assignments(db, self.ORG, first)[0]
        declined = client.post(
            f"/api/v1/assignments/{assignment.id}/decline",
            json={"decline_reason": "away that weekend"},
            headers=vol_headers,
        )
        assert declined.status_code == 200, declined.text

        second = _solve(client, headers, self.ORG)
        refused = _publish(client, headers, second)

        assert refused.status_code == 409, refused.text
        assert "declined" in refused.json()["detail"].lower()
        db.expire_all()
        assert _published_solution_ids(db, self.ORG) == [first]


# ---------------------------------------------------------------------------
# Tenancy
# ---------------------------------------------------------------------------


@pytest.mark.no_mock_auth
def test_recovery_in_one_organization_leaves_the_other_live(client, db):
    """One tenant's unpublish/republish never touches another tenant's schedule."""
    mine_org = "recovery-tenant-mine"
    theirs_org = "recovery-tenant-theirs"
    my_headers, _, _ = _one_event_one_usher(client, mine_org, event_id="recovery-tenant-mine-ev")
    their_headers, their_names, _ = _one_event_one_usher(
        client, theirs_org, event_id="recovery-tenant-theirs-ev"
    )
    their_vol_headers = _volunteer_headers(client, theirs_org, their_names[0])

    mine = _solve(client, my_headers, mine_org)
    theirs = _solve(client, their_headers, theirs_org)
    assert _publish(client, my_headers, mine).status_code == 200
    assert _publish(client, their_headers, theirs).status_code == 200

    assert _unpublish(client, my_headers, mine).status_code == 200

    db.expire_all()
    assert _published_solution_ids(db, mine_org) == []
    assert _published_solution_ids(db, theirs_org) == [theirs]
    assert len(_my_assignments(client, their_vol_headers)) == 1
    assert len(_notifications(db, theirs_org)) == 1

    # And the other tenant's admin cannot reach into this recovery.
    assert _publish(client, their_headers, mine).status_code == 404
    assert _rollback(client, their_headers, mine).status_code == 404
