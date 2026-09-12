"""Unpublished solver assignments must not be visible or actionable by members."""

import pytest

from api.models import Assignment, Solution
from tests.web.conftest import seed_person
from tests.web.test_schedule import _seed_assignment


@pytest.mark.parametrize("published", [False, True])
def test_member_publication_boundary(client, db, published):
    person = seed_person(db)
    _seed_assignment(db, person)
    solution = Solution(
        org_id=person.org_id,
        hard_violations=0,
        soft_score=0,
        health_score=100,
        is_published=published,
    )
    db.add(solution)
    db.flush()
    assignment = db.query(Assignment).filter(Assignment.person_id == person.id).one()
    assignment.solution_id = solution.id
    assignment.status = "pending"
    db.commit()
    client.post("/auth/login", data={"email": person.email, "password": "WebPass123!"})
    response = client.get("/v/schedule")
    assert ("Sunday Service" in response.text) is published
    assert client.get(f"/v/schedule/{assignment.id}").status_code == (200 if published else 404)
    assert client.post(f"/v/schedule/{assignment.id}/accept").status_code == (
        200 if published else 404
    )
    db.refresh(assignment)
    assert assignment.status == ("confirmed" if published else "pending")
