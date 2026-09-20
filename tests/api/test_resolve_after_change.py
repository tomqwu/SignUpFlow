"""Re-solving after a roster change, and overriding what the solver decided.

Two coverage gaps meet here, both about what happens *after* a schedule exists.

Scenario 13 (qualification removed): `test_solution_publication_safety.py`
proves an administrator's qualification removal reopens future live work and
leaves past work alone. It stops there. Nothing proved the next *solve* honours
the removal, which is the half a coordinator actually feels: run the scheduler
again and the person must not reappear in the role they lost.

Scenario 8 (manual override): manual assignment is covered elsewhere, but only
into slots that were empty or manually filled. Nothing overrode a placement the
*solver* made, and nothing pinned what a later solve does to that override.
These tests pin the real behaviour, including the part that is a hazard rather
than a feature: a later solve neither sees nor preserves the override.

Two boundaries drive the shape of the tests below:

- A solver placement only becomes live work once its solution is published
  (`api/services/assignment_visibility.py`), so overriding a draft placement is
  impossible by design: the roster edit endpoints cannot see it. Publishing
  first is therefore part of the override scenario, not incidental setup.
- Each solve writes a brand new `Solution` with its own assignments. Manual
  assignments carry `solution_id IS NULL` and live outside any solution, which
  is what makes the interaction between the two worth pinning.
"""

from datetime import datetime, timedelta

import pytest

from api.models import Assignment, Event
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

# Events sit three weeks out; the solve window brackets them generously.
EVENT_DAYS_OUT = 21
WINDOW_START_DAYS = 14
WINDOW_END_DAYS = 45


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


def _solve(client, headers: dict, org_id: str) -> dict:
    """Run the solver over the window containing the seeded events."""
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
    return response.json()


def _solution_roster(db, org_id: str, solution_id: int) -> set[tuple[str, str, str]]:
    """(event_id, person_id, role) triples belonging to one solution, org-scoped."""
    rows = (
        db.query(Assignment)
        .join(Event, Assignment.event_id == Event.id)
        .filter(Event.org_id == org_id, Assignment.solution_id == solution_id)
        .all()
    )
    return {(row.event_id, row.person_id, row.role) for row in rows}


def _manual_roster(db, org_id: str) -> set[tuple[str, str, str]]:
    """(event_id, person_id, role) triples that belong to no solution."""
    rows = (
        db.query(Assignment)
        .join(Event, Assignment.event_id == Event.id)
        .filter(Event.org_id == org_id, Assignment.solution_id.is_(None))
        .all()
    )
    return {(row.event_id, row.person_id, row.role) for row in rows}


def _assign(client, headers: dict, event_id: str, person_id: str, action: str, role: str):
    return client.post(
        f"/api/v1/events/{event_id}/assignments",
        json={"person_id": person_id, "action": action, "role": role},
        headers=headers,
    )


@pytest.mark.no_mock_auth
class TestResolveAfterQualificationChange:
    """Scenario 13: the next schedule must respect a removed qualification."""

    ORG = "requalify-org"

    def _setup(self, client):
        headers = _admin(client, self.ORG)
        first = _volunteer(client, headers, self.ORG, "avery", ["children_leader"])
        second = _volunteer(client, headers, self.ORG, "blake", ["children_leader"])
        seed_event(
            client,
            headers,
            self.ORG,
            "kids-class",
            event_type="Kids Class",
            days_from_now=EVENT_DAYS_OUT,
            role_counts={"children_leader": 1},
        )
        return headers, {first, second}

    def test_fresh_solve_excludes_the_person_who_lost_the_qualification(self, client, db):
        """Remove the qualification, solve again, and they are not placed in that role."""
        headers, everyone = self._setup(client)

        first_solution = _solve(client, headers, self.ORG)["solution_id"]
        placed = _solution_roster(db, self.ORG, first_solution)
        assert len(placed) == 1, "solver should have staffed the single children_leader slot"
        (event_id, dropped, role) = next(iter(placed))
        assert role == "children_leader"

        removal = client.put(
            f"/api/v1/people/{dropped}",
            json={"roles": ["volunteer"]},
            headers=headers,
        )
        assert removal.status_code == 200, removal.text
        assert removal.json()["roles"] == ["volunteer"]

        second_solution = _solve(client, headers, self.ORG)["solution_id"]
        assert second_solution != first_solution

        reroster = _solution_roster(db, self.ORG, second_solution)
        assert dropped not in {
            person_id for (_, person_id, _) in reroster
        }, "the solver placed someone who no longer holds the children_leader qualification"
        # The slot is still required, so the remaining qualified volunteer takes it.
        remaining = (everyone - {dropped}).pop()
        assert reroster == {(event_id, remaining, "children_leader")}

    def test_fresh_solve_leaves_the_role_open_when_nobody_is_qualified(self, client, db):
        """With the last qualified person demoted the solve succeeds but understaffs."""
        headers, everyone = self._setup(client)
        for person_id in everyone:
            demoted = client.put(
                f"/api/v1/people/{person_id}",
                json={"roles": ["volunteer"]},
                headers=headers,
            )
            assert demoted.status_code == 200, demoted.text

        result = _solve(client, headers, self.ORG)

        # The solver reports the shortage as a hard violation rather than
        # inventing a placement or failing the request.
        assert _solution_roster(db, self.ORG, result["solution_id"]) == set()
        assert result["metrics"]["hard_violations"] >= 1


@pytest.mark.no_mock_auth
class TestManualOverrideOfSolverPlacement:
    """Scenario 8: replacing the person the solver chose, and what a re-solve does."""

    ORG = "override-org"

    def _setup(self, client):
        headers = _admin(client, self.ORG)
        first = _volunteer(client, headers, self.ORG, "casey", ["usher"])
        second = _volunteer(client, headers, self.ORG, "dakota", ["usher"])
        seed_event(
            client,
            headers,
            self.ORG,
            "sunday-service",
            event_type="Sunday Service",
            days_from_now=EVENT_DAYS_OUT,
            role_counts={"usher": 1},
        )
        return headers, {first, second}

    def _published_placement(self, client, db, headers) -> tuple[int, str, str]:
        """Solve, publish, and return (solution_id, event_id, person the solver chose)."""
        solution_id = _solve(client, headers, self.ORG)["solution_id"]
        published = client.post(f"/api/v1/solutions/{solution_id}/publish", headers=headers)
        assert published.status_code == 200, published.text
        roster = _solution_roster(db, self.ORG, solution_id)
        assert len(roster) == 1
        (event_id, chosen, _role) = next(iter(roster))
        return solution_id, event_id, chosen

    def test_draft_solver_placement_cannot_be_overridden_before_publication(self, client, db):
        """A draft placement is not live work, so the roster editor cannot see it."""
        headers, _ = self._setup(client)
        solution_id = _solve(client, headers, self.ORG)["solution_id"]
        (event_id, chosen, _role) = next(iter(_solution_roster(db, self.ORG, solution_id)))

        response = _assign(client, headers, event_id, chosen, "unassign", "usher")

        assert response.status_code == 404
        assert "not assigned" in response.json()["detail"].lower()

    def test_admin_replaces_the_person_the_solver_placed(self, client, db):
        """Unassign the solver's pick and assign a different qualified volunteer."""
        headers, everyone = self._setup(client)
        solution_id, event_id, chosen = self._published_placement(client, db, headers)
        replacement = (everyone - {chosen}).pop()

        removed = _assign(client, headers, event_id, chosen, "unassign", "usher")
        assert removed.status_code == 200, removed.text

        added = _assign(client, headers, event_id, replacement, "assign", "usher")
        assert added.status_code == 200, added.text

        # The solver's row is gone from the published solution; the override
        # stands on its own with solution_id NULL.
        assert _solution_roster(db, self.ORG, solution_id) == set()
        assert _manual_roster(db, self.ORG) == {(event_id, replacement, "usher")}

    def test_override_cannot_exceed_the_role_capacity(self, client, db):
        """The replacement only fits because the solver's pick was removed first."""
        headers, everyone = self._setup(client)
        _solution_id, event_id, chosen = self._published_placement(client, db, headers)
        replacement = (everyone - {chosen}).pop()

        refused = _assign(client, headers, event_id, replacement, "assign", "usher")

        assert refused.status_code == 409
        assert "fully staffed" in refused.json()["detail"].lower()

    def test_later_solve_ignores_the_manual_override(self, client, db):
        """Pins today's behaviour: a re-solve neither sees nor preserves the override.

        The override survives as its own row, but the fresh solution re-places the
        very person the administrator removed. Nothing about the manual decision
        reaches the solve, so the new draft and the override together describe two
        ushers for a one-usher role — which is exactly what stops the new draft
        from going live in the companion test below.
        """
        headers, everyone = self._setup(client)
        _first_solution, event_id, chosen = self._published_placement(client, db, headers)
        replacement = (everyone - {chosen}).pop()
        assert _assign(client, headers, event_id, chosen, "unassign", "usher").status_code == 200
        assert _assign(client, headers, event_id, replacement, "assign", "usher").status_code == 200

        second_solution = _solve(client, headers, self.ORG)["solution_id"]

        # The manual override is untouched by the solve.
        assert _manual_roster(db, self.ORG) == {(event_id, replacement, "usher")}
        # ...but the new draft ignores it and re-places the person who was removed.
        assert _solution_roster(db, self.ORG, second_solution) == {(event_id, chosen, "usher")}

    def test_the_later_solution_cannot_be_published_over_the_override(self, client, db):
        """Pins the dead end the previous test sets up.

        Publication counts manual assignments alongside the candidate solution's
        own, so the re-placed solver pick plus the surviving override read as two
        ushers in a one-usher role and publication refuses. The override is not
        mentioned in the refusal, so from the coordinator's side the next
        schedule simply cannot go live until they undo their own override or
        regenerate. Nothing here says that is the intended design; the assertions
        record what the system does today.
        """
        headers, everyone = self._setup(client)
        first_solution, event_id, chosen = self._published_placement(client, db, headers)
        replacement = (everyone - {chosen}).pop()
        assert _assign(client, headers, event_id, chosen, "unassign", "usher").status_code == 200
        assert _assign(client, headers, event_id, replacement, "assign", "usher").status_code == 200
        second_solution = _solve(client, headers, self.ORG)["solution_id"]

        published = client.post(f"/api/v1/solutions/{second_solution}/publish", headers=headers)

        assert published.status_code == 409
        detail = published.json()["detail"]
        assert "role capacity exceeded" in detail.lower()
        assert f"{event_id}:usher" in detail
        # The refusal changes nothing: the override still stands, the new
        # solution stays a draft, and the older solution keeps the publication.
        assert _manual_roster(db, self.ORG) == {(event_id, replacement, "usher")}
        solutions = client.get(f"/api/v1/solutions/?org_id={self.ORG}", headers=headers)
        assert solutions.status_code == 200, solutions.text
        published_state = {row["id"]: row["is_published"] for row in solutions.json()["items"]}
        assert published_state[first_solution] is True
        assert published_state[second_solution] is False
