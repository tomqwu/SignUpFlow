"""Solution stats tests for /api/v1/solutions/{id}/stats.

Sprint 6 PR 6.5 adds an admin-only stats endpoint that returns derived
metrics for any solution in the caller's org:

- ``fairness`` — stdev, per-person counts, and a histogram (count → num_people).
- ``stability`` — moves_from_published and affected_persons (from 6.1).
- ``workload`` — max/min/median events per person, totals.

The values come from the persisted ``Solution.metrics`` dict (populated at
solve time in ``api/routers/solver.py``) plus aggregations computed at
request time from the same dict.
"""

import pytest

from api.models import Solution
from api.timeutils import utcnow
from tests.api.conftest import auth_headers, seed_org, seed_user


def _admin_for(client, org_id: str, suffix: str):
    seed_user(
        client,
        org_id,
        email=f"admin-{suffix}@o.org",
        name="Admin",
        password="AdminPass1!",
    )
    return auth_headers(client, email=f"admin-{suffix}@o.org", password="AdminPass1!")


def _seed_solution_with_metrics(
    db,
    org_id: str,
    *,
    per_person_counts: dict[str, int],
    moves_from_published: int = 0,
    affected_persons: int = 0,
) -> Solution:
    sol = Solution(
        org_id=org_id,
        solve_ms=12.5,
        hard_violations=0,
        soft_score=2.0,
        health_score=98.0,
        metrics={
            "fairness": {
                "stdev": 0.5,
                "per_person_counts": per_person_counts,
            },
            "stability": {
                "moves_from_published": moves_from_published,
                "affected_persons": affected_persons,
            },
        },
    )
    db.add(sol)
    db.commit()
    db.refresh(sol)
    return sol


@pytest.mark.no_mock_auth
class TestSolutionStats:
    def test_admin_can_get_stats(self, client, db):
        org_id = "stats-ok"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "ok")
        sol = _seed_solution_with_metrics(
            db,
            org_id,
            per_person_counts={"p1": 3, "p2": 2, "p3": 2, "p4": 1},
            moves_from_published=4,
            affected_persons=2,
        )

        resp = client.get(f"/api/v1/solutions/{sol.id}/stats", headers=hdrs)
        assert resp.status_code == 200, resp.text

        body = resp.json()
        assert body["solution_id"] == sol.id

        # Fairness — exposes stdev, per-person counts, and a histogram.
        assert body["fairness"]["stdev"] == 0.5
        assert body["fairness"]["per_person_counts"] == {
            "p1": 3,
            "p2": 2,
            "p3": 2,
            "p4": 1,
        }
        # Histogram: count → num_people_with_that_count.
        assert body["fairness"]["histogram"] == {"1": 1, "2": 2, "3": 1}

        # Stability — pass-through from the persisted metrics.
        assert body["stability"]["moves_from_published"] == 4
        assert body["stability"]["affected_persons"] == 2

        # Workload — derived aggregations on per_person_counts.
        assert body["workload"]["max_events_per_person"] == 3
        assert body["workload"]["min_events_per_person"] == 1
        assert body["workload"]["median_events_per_person"] == 2.0
        assert body["workload"]["total_events_assigned"] == 8
        assert body["workload"]["distinct_persons_assigned"] == 4

    def test_volunteer_blocked(self, client, db):
        org_id = "stats-vol"
        seed_org(client, org_id)
        _admin_for(client, org_id, "vol-admin")
        seed_user(
            client,
            org_id,
            email="vol@o.org",
            name="Vol",
            password="VolPass1!",
            roles=["volunteer"],
        )
        vol_hdrs = auth_headers(client, email="vol@o.org", password="VolPass1!")
        sol = _seed_solution_with_metrics(db, org_id, per_person_counts={"p1": 1})

        resp = client.get(f"/api/v1/solutions/{sol.id}/stats", headers=vol_hdrs)
        assert resp.status_code == 403

    def test_cross_org_blocked(self, client, db):
        seed_org(client, "stats-a")
        seed_org(client, "stats-b")
        a_hdrs = _admin_for(client, "stats-a", "a")
        sol_b = _seed_solution_with_metrics(db, "stats-b", per_person_counts={"p1": 1})

        resp = client.get(f"/api/v1/solutions/{sol_b.id}/stats", headers=a_hdrs)
        assert resp.status_code == 403

    def test_missing_solution_404(self, client, db):
        org_id = "stats-missing"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "missing")

        resp = client.get("/api/v1/solutions/9999999/stats", headers=hdrs)
        assert resp.status_code == 404

    def test_requires_auth(self, client, db):
        org_id = "stats-noauth"
        seed_org(client, org_id)
        _admin_for(client, org_id, "noauth")
        sol = _seed_solution_with_metrics(db, org_id, per_person_counts={"p1": 1})

        resp = client.get(f"/api/v1/solutions/{sol.id}/stats")
        assert resp.status_code in (401, 403)

    def test_empty_per_person_counts(self, client, db):
        """A solution with no assigned people returns sensible zero/empty values."""
        org_id = "stats-empty"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "empty")
        sol = _seed_solution_with_metrics(db, org_id, per_person_counts={})

        resp = client.get(f"/api/v1/solutions/{sol.id}/stats", headers=hdrs)
        assert resp.status_code == 200
        body = resp.json()
        assert body["fairness"]["histogram"] == {}
        assert body["workload"]["max_events_per_person"] == 0
        assert body["workload"]["min_events_per_person"] == 0
        assert body["workload"]["median_events_per_person"] == 0.0
        assert body["workload"]["total_events_assigned"] == 0
        assert body["workload"]["distinct_persons_assigned"] == 0

    def test_missing_metrics_keys_treated_as_zero(self, client, db):
        """A solution persisted before 6.1 has no stability metrics; default to 0."""
        org_id = "stats-legacy"
        seed_org(client, org_id)
        hdrs = _admin_for(client, org_id, "legacy")

        sol = Solution(
            org_id=org_id,
            solve_ms=10.0,
            hard_violations=0,
            soft_score=1.0,
            health_score=99.0,
            metrics={},  # no fairness or stability keys
            is_published=False,
            published_at=None,
        )
        sol.created_at = utcnow()
        db.add(sol)
        db.commit()
        db.refresh(sol)

        resp = client.get(f"/api/v1/solutions/{sol.id}/stats", headers=hdrs)
        assert resp.status_code == 200
        body = resp.json()
        assert body["stability"]["moves_from_published"] == 0
        assert body["stability"]["affected_persons"] == 0
        assert body["fairness"]["stdev"] == 0.0
        assert body["fairness"]["per_person_counts"] == {}
        assert body["fairness"]["histogram"] == {}
